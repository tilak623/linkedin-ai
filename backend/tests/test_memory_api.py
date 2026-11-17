import os
import sqlite3
import tempfile
import unittest

from fastapi.testclient import TestClient

from backend.app.core.db import db
from backend.app.main import app


class TestProfessionalMemoryApi(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = db.db_path
        db.db_path = os.path.join(self.temp_dir.name, "memory-test.db")
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

    def test_onboarding_persists_profile_and_initial_skills(self):
        auth_before = self.client.get("/api/v1/auth/me")
        self.assertFalse(auth_before.json()["data"]["onboarding_completed"])
        response = self.client.post(
            "/api/v1/profile/onboard",
            json={
                "full_name": "Test Engineer",
                "headline": "Backend Developer",
                "career_direction": "Reliable local-first tools",
                "initial_skills": [
                    {
                        "name": "Python",
                        "proficiency_level": "implemented",
                        "category": "Backend",
                        "evidence_notes": "Built a local service",
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["headline"], "Backend Developer")
        auth_after = self.client.get("/api/v1/auth/me")
        self.assertTrue(auth_after.json()["data"]["onboarding_completed"])
        profile = self.client.get("/api/v1/profile")
        self.assertEqual(profile.json()["data"]["career_direction"], "Reliable local-first tools")
        skills = self.client.get("/api/v1/memory/skills").json()["data"]
        self.assertEqual(len(skills), 1)
        self.assertEqual(skills[0]["proficiency_level"], "implemented")
        export = self.client.get("/api/v1/memory/export")
        self.assertEqual(export.status_code, 200)
        self.assertEqual(export.json()["data"]["user"]["full_name"], "Test Engineer")
        self.assertEqual(export.json()["data"]["skills"][0]["name"], "Python")

    def test_skill_duplicate_detection_update_delete_and_search(self):
        create = self.client.post(
            "/api/v1/memory/skills",
            json={
                "name": "SQLite",
                "proficiency_level": "studied",
                "category": "Data",
                "evidence_notes": "Reviewed connection concurrency behavior",
            },
        )
        self.assertEqual(create.status_code, 201)
        skill_id = create.json()["data"]["id"]

        duplicate = self.client.post(
            "/api/v1/memory/skills",
            json={"name": "sqlite", "proficiency_level": "discovered"},
        )
        self.assertEqual(duplicate.status_code, 409)

        search = self.client.get("/api/v1/memory/search", params={"q": "connection concurrency"})
        self.assertEqual(search.status_code, 200)
        self.assertEqual(search.json()["data"][0]["entity_id"], skill_id)

        update = self.client.patch(
            f"/api/v1/memory/skills/{skill_id}",
            json={"proficiency_level": "implemented", "evidence_notes": "Built and tested a connection manager"},
        )
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.json()["data"]["proficiency_level"], "implemented")

        delete = self.client.delete(f"/api/v1/memory/skills/{skill_id}")
        self.assertTrue(delete.json()["data"]["deleted"])
        self.assertEqual(self.client.get("/api/v1/memory/skills").json()["data"], [])

    def test_projects_and_learning_milestones_support_crud(self):
        unsafe_url = self.client.post(
            "/api/v1/memory/projects",
            json={"title": "Bad link", "github_url": "javascript:alert(1)"},
        )
        self.assertEqual(unsafe_url.status_code, 422)

        project = self.client.post(
            "/api/v1/memory/projects",
            json={
                "title": "Local-first assistant",
                "maturity": "in_development",
                "description": "A tool that stores professional notes locally",
                "tech_stack": ["Python", "SQLite"],
            },
        )
        self.assertEqual(project.status_code, 201)
        project_id = project.json()["data"]["id"]
        self.assertEqual(project.json()["data"]["tech_stack"], ["Python", "SQLite"])
        duplicate_project = self.client.post(
            "/api/v1/memory/projects",
            json={"title": "local-first assistant", "maturity": "planned"},
        )
        self.assertEqual(duplicate_project.status_code, 409)
        self.assertEqual(
            self.client.patch(
                f"/api/v1/memory/projects/{project_id}",
                json={"maturity": "completed"},
            ).json()["data"]["maturity"],
            "completed",
        )
        db.init_db()
        search = self.client.get("/api/v1/memory/search", params={"q": "local first assistant"})
        self.assertEqual(search.json()["data"][0]["entity_id"], project_id)
        self.assertTrue(self.client.delete(f"/api/v1/memory/projects/{project_id}").json()["data"]["deleted"])

        milestone = self.client.post(
            "/api/v1/memory/milestones",
            json={
                "title": "Understood SQLite indexing",
                "milestone_date": "2026-11-17",
                "lessons_learned": "Indexes speed up common lookups",
            },
        )
        self.assertEqual(milestone.status_code, 201)
        milestone_id = milestone.json()["data"]["id"]
        self.assertEqual(
            self.client.patch(
                f"/api/v1/memory/milestones/{milestone_id}",
                json={"category": "Database learning"},
            ).json()["data"]["category"],
            "Database learning",
        )
        self.assertTrue(self.client.delete(f"/api/v1/memory/milestones/{milestone_id}").json()["data"]["deleted"])


if __name__ == "__main__":
    unittest.main()
