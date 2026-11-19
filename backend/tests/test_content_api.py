import io
import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from PIL import Image
import httpx

from backend.app.core.config import settings
from backend.app.core.db import DEFAULT_USER_ID, db
from backend.app.main import app
from backend.app.api.v1.content import _create_daily_draft, recover_interrupted_posts, run_scheduler_tick


class TestContentWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = db.db_path
        db.db_path = os.path.join(self.temp_dir.name, "content-test.db")
        connection = sqlite3.connect(db.db_path)
        connection.execute(
            """CREATE TABLE users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )"""
        )
        connection.commit()
        connection.close()
        self.settings_patch = patch.multiple(
            settings,
            LINKEDIN_CLIENT_ID="test-client",
            LINKEDIN_CLIENT_SECRET="test-secret",
            LINKEDIN_TOKEN_ENCRYPTION_KEY="configured-test-key",
            GEMINI_API_KEY="test-gemini-key",
            ENABLE_BACKGROUND_SCHEDULER=False,
            SCHEDULER_TRIGGER_TOKEN="test-scheduler-token",
        )
        self.settings_patch.start()
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        self.settings_patch.stop()
        db.db_path = self.original_db_path
        self.temp_dir.cleanup()

    def add_interview_evidence(self, summary="I learned how to test the Python changes in my project."):
        interview_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        db.execute(
            """INSERT INTO interviews
               (id, user_id, interview_date, mode, completed, summary, extracted_topics, created_at, updated_at)
               VALUES (?, ?, ?, 'text', 1, ?, '[]', ?, ?)""",
            (
                interview_id, DEFAULT_USER_ID, datetime.now().date().isoformat(),
                summary, now, now,
            ),
        )

    def add_linkedin_connection(self):
        now = datetime.now(timezone.utc)
        db.execute(
            """INSERT INTO linkedin_connections
               (user_id, encrypted_token, person_urn, expires_at, created_at, updated_at)
               VALUES (?, 'encrypted-test-token', 'urn:li:person:test-member', ?, ?, ?)""",
            (
                DEFAULT_USER_ID, (now + timedelta(days=1)).isoformat(),
                now.isoformat(), now.isoformat(),
            ),
        )

    def test_generation_requires_evidence_and_never_uses_seed_claims(self):
        missing = self.client.post("/api/v1/content/generate")
        self.assertEqual(missing.status_code, 409)

        self.add_interview_evidence()
        response = self.client.post("/api/v1/content/generate")
        self.assertEqual(response.status_code, 201)
        post = response.json()["data"]
        self.assertEqual(post["status"], "draft")
        self.assertIn("I learned how to test", post["final_content"])
        self.assertNotIn("sub-millisecond", post["final_content"])

    def test_ai_humanize_creates_an_editable_review_required_draft(self):
        generated = {
            "title": "A small lesson from today",
            "content": "I learned to verify my changes with focused tests.",
        }
        provider_response = httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": json.dumps(generated)}]}}]},
        )
        with patch("backend.app.api.v1.content.httpx.post", return_value=provider_response) as provider:
            response = self.client.post(
                "/api/v1/content/humanize",
                json={"source_text": "I learned to test my changes today."},
            )

        self.assertEqual(response.status_code, 201)
        post = response.json()["data"]
        self.assertEqual(post["status"], "draft")
        self.assertEqual(post["final_content"], generated["content"])
        self.assertIn("I learned to test my changes today", provider.call_args.kwargs["json"]["contents"][0]["parts"][0]["text"])
        self.assertEqual(
            db.fetch_one("SELECT status FROM content_posts WHERE id = ?", (post["id"],))["status"],
            "draft",
        )

    def test_media_upload_validates_images_and_attaches_to_post(self):
        self.add_interview_evidence()
        post = self.client.post("/api/v1/content/generate").json()["data"]
        image_bytes = io.BytesIO()
        Image.new("RGB", (4, 4), color="blue").save(image_bytes, format="PNG")

        uploaded = self.client.post(
            f"/api/v1/content/posts/{post['id']}/media",
            files={"file": ("proof.png", image_bytes.getvalue(), "image/png")},
        )
        self.assertEqual(uploaded.status_code, 201)
        media = uploaded.json()["data"]
        preview = self.client.get(media["preview_url"])
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(preview.headers["content-type"], "image/png")
        self.assertEqual(preview.content, image_bytes.getvalue())

        duplicate = self.client.post(
            f"/api/v1/content/posts/{post['id']}/media",
            files={"file": ("proof.png", image_bytes.getvalue(), "image/png")},
        )
        self.assertEqual(duplicate.status_code, 409)

        with patch("backend.app.api.v1.content.publish_linkedin_post", return_value="urn:li:share:post-1") as publish:
            now = datetime.now(timezone.utc)
            db.execute(
                "UPDATE content_posts SET status = 'scheduled', scheduled_for = ? WHERE id = ?",
                ((now - timedelta(minutes=1)).isoformat(), post["id"]),
            )
            run_scheduler_tick(now)
        publish.assert_called_once()
        published_media = publish.call_args.args[1]
        self.assertEqual(published_media[0]["filename"], "proof.png")
        self.assertEqual(published_media[0]["content"], image_bytes.getvalue())

    def test_edit_and_approval_create_audited_scheduled_public_post(self):
        self.add_interview_evidence()
        self.add_linkedin_connection()
        draft = self.client.post("/api/v1/content/generate").json()["data"]

        refused = self.client.post(
            f"/api/v1/content/posts/{draft['id']}/approve",
            json={"confirm": False},
        )
        self.assertEqual(refused.status_code, 400)

        edited = self.client.patch(
            f"/api/v1/content/posts/{draft['id']}",
            json={"title": "My learning note", "final_content": "A verified learning note."},
        )
        self.assertEqual(edited.status_code, 200)
        approved = self.client.post(
            f"/api/v1/content/posts/{draft['id']}/approve",
            json={"confirm": True},
        )
        self.assertEqual(approved.status_code, 200)
        self.assertEqual(approved.json()["data"]["status"], "scheduled")
        self.assertTrue(approved.json()["data"]["approved_at"])
        self.assertEqual(
            db.fetch_one(
                "SELECT action_type FROM audit_logs WHERE action_type = 'linkedin_post_approved'"
            )["action_type"],
            "linkedin_post_approved",
        )
        self.assertEqual(
            self.client.patch(
                f"/api/v1/content/posts/{draft['id']}",
                json={"title": "Changed", "final_content": "A different post."},
            ).status_code,
            409,
        )

    def test_scheduler_publishes_once_and_holds_posts_that_are_too_late(self):
        self.add_linkedin_connection()
        now = datetime.now(timezone.utc)
        due_id = str(uuid4())
        late_id = str(uuid4())
        for post_id, scheduled_for in (
            (due_id, (now - timedelta(minutes=1)).isoformat()),
            (late_id, (now - timedelta(minutes=20)).isoformat()),
        ):
            db.execute(
                """INSERT INTO content_posts
                   (id, user_id, title, content_category, final_content, status,
                    scheduled_for, approval_log, created_at, updated_at)
                   VALUES (?, ?, 'Scheduled evidence post', 'learning_experience',
                           'Approved exact text', 'scheduled', ?, '{}', ?, ?)""",
                (post_id, DEFAULT_USER_ID, scheduled_for, now.isoformat(), now.isoformat()),
            )

        with patch("backend.app.api.v1.content.publish_linkedin_post", return_value="urn:li:share:post-1") as publish:
            run_scheduler_tick(now)
            run_scheduler_tick(now + timedelta(seconds=1))
        publish.assert_called_once_with("Approved exact text")
        self.assertEqual(db.fetch_one("SELECT status FROM content_posts WHERE id = ?", (due_id,))["status"], "published")
        self.assertEqual(db.fetch_one("SELECT status FROM content_posts WHERE id = ?", (late_id,))["status"], "missed_schedule")

    def test_external_scheduler_trigger_requires_its_secret(self):
        with patch("backend.app.api.v1.content.run_scheduler_tick") as tick:
            denied = self.client.post(
                "/api/v1/content/scheduler/tick",
                headers={"Authorization": "Bearer wrong-token"},
            )
            accepted = self.client.post(
                "/api/v1/content/scheduler/tick",
                headers={"Authorization": "Bearer test-scheduler-token"},
            )

        self.assertEqual(denied.status_code, 401)
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.json()["data"]["triggered"], True)
        tick.assert_called_once_with()

    def test_automatic_daily_generation_is_idempotent(self):
        self.add_interview_evidence()
        run_date = datetime.now().date()
        _create_daily_draft(run_date)
        _create_daily_draft(run_date)
        _create_daily_draft(run_date + timedelta(days=1))
        self.assertEqual(
            db.fetch_one("SELECT COUNT(*) AS count FROM daily_post_runs WHERE run_date = ?", (run_date.isoformat(),))["count"],
            1,
        )
        self.assertEqual(db.fetch_one("SELECT COUNT(*) AS count FROM content_posts")["count"], 1)

    def test_missed_post_requires_a_new_approval_and_interrupted_publish_is_held(self):
        self.add_linkedin_connection()
        now = datetime.now(timezone.utc).isoformat()
        missed_id = str(uuid4())
        interrupted_id = str(uuid4())
        for post_id, post_status in ((missed_id, "missed_schedule"), (interrupted_id, "publishing")):
            db.execute(
                """INSERT INTO content_posts
                   (id, user_id, title, content_category, final_content, status,
                    approval_log, created_at, updated_at)
                   VALUES (?, ?, 'Evidence post', 'learning_experience',
                           'Exact approved text', ?, '{}', ?, ?)""",
                (post_id, DEFAULT_USER_ID, post_status, now, now),
            )

        rescheduled = self.client.post(
            f"/api/v1/content/posts/{missed_id}/reschedule",
            json={"confirm": True},
        )
        self.assertEqual(rescheduled.status_code, 200)
        self.assertEqual(rescheduled.json()["data"]["status"], "scheduled")
        self.assertEqual(len(json.loads(db.fetch_one(
            "SELECT approval_log FROM content_posts WHERE id = ?", (missed_id,)
        )["approval_log"])["previous_approvals"]), 1)

        recover_interrupted_posts()
        self.assertEqual(
            db.fetch_one("SELECT status FROM content_posts WHERE id = ?", (interrupted_id,))["status"],
            "publish_failed",
        )


if __name__ == "__main__":
    unittest.main()
