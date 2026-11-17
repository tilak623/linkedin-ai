import os
import sqlite3
import tempfile
import unittest

from fastapi.testclient import TestClient

from backend.app.core.db import db
from backend.app.main import app


class TestInterviewApi(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = db.db_path
        db.db_path = os.path.join(self.temp_dir.name, "interview-test.db")
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
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        db.db_path = self.original_db_path
        self.temp_dir.cleanup()

    def test_interview_resumes_persists_adaptive_turns_and_completes(self):
        self.assertIsNone(self.client.get("/api/v1/interviews/today").json()["data"])
        started = self.client.post("/api/v1/interviews/start", json={"mode": "text"})
        self.assertEqual(started.status_code, 200)
        session_id = started.json()["data"]["id"]
        self.assertEqual(started.json()["data"]["messages"][0]["sender"], "ai")
        self.assertEqual(self.client.get("/api/v1/interviews/today").json()["data"]["id"], session_id)

        resumed = self.client.post("/api/v1/interviews/start", json={"mode": "voice"})
        self.assertEqual(resumed.json()["data"]["id"], session_id)
        self.assertEqual(resumed.json()["data"]["mode"], "text")

        first_turn = self.client.post(
            f"/api/v1/interviews/{session_id}/turn",
            json={"user_response": "I built a small Python feature and tested it."},
        )
        self.assertEqual(first_turn.status_code, 200)
        self.assertFalse(first_turn.json()["data"]["session"]["completed"])

        second_turn = self.client.post(
            f"/api/v1/interviews/{session_id}/turn",
            json={"user_response": "The issue was a race condition and I fixed it by isolating writes."},
        )
        self.assertEqual(second_turn.status_code, 200)
        self.assertIn("investigate or resolve", second_turn.json()["data"]["session"]["messages"][-1]["content"])

        third_turn = self.client.post(
            f"/api/v1/interviews/{session_id}/turn",
            json={"user_response": "I learned to test overlapping transactions and document the behavior."},
        )
        self.assertTrue(third_turn.json()["data"]["session"]["completed"])
        self.assertIn("I learned", third_turn.json()["data"]["session"]["summary"])

        persisted = self.client.get(f"/api/v1/interviews/{session_id}")
        self.assertEqual(len(persisted.json()["data"]["messages"]), 6)
        interview_search = self.client.get("/api/v1/memory/search", params={"q": "race condition"})
        self.assertEqual(interview_search.json()["data"][0]["entity_type"], "interviews")
        repeated_turn = self.client.post(
            f"/api/v1/interviews/{session_id}/turn",
            json={"user_response": "One more answer"},
        )
        self.assertEqual(repeated_turn.status_code, 409)

    def test_no_progress_completes_without_content_opportunity(self):
        started = self.client.post("/api/v1/interviews/start", json={"mode": "text"})
        session_id = started.json()["data"]["id"]
        response = self.client.post(
            f"/api/v1/interviews/{session_id}/turn",
            json={"user_response": "Nothing significant."},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["data"]["session"]["completed"])
        self.assertEqual(response.json()["data"]["content_opportunity"], "none")


if __name__ == "__main__":
    unittest.main()
