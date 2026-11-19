import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.core.db import db
from backend.app.core.session_auth import SESSION_COOKIE_NAME
from backend.app.main import app
from backend.app.api.v1.auth import _LOGIN_FAILURES


class TestAppPasswordSecurity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = db.db_path
        db.db_path = os.path.join(self.temp_dir.name, "auth-test.db")
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
            APP_ADMIN_PASSWORD="correct horse battery staple",
            APP_SESSION_SECRET="unit-test-session-secret",
            ENVIRONMENT="test",
            ENABLE_BACKGROUND_SCHEDULER=False,
        )
        self.settings_patch.start()
        _LOGIN_FAILURES.clear()
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        self.settings_patch.stop()
        db.db_path = self.original_db_path
        self.temp_dir.cleanup()

    def test_api_is_private_until_password_login_and_logout_revokes_cookie(self):
        self.assertEqual(self.client.get("/api/v1/settings").status_code, 401)
        self.assertFalse(self.client.get("/api/v1/auth/me").json()["data"]["authenticated"])
        self.assertEqual(
            self.client.post("/api/v1/auth/login", json={"password": "wrong"}).status_code,
            401,
        )

        login = self.client.post(
            "/api/v1/auth/login",
            json={"password": "correct horse battery staple"},
        )
        self.assertEqual(login.status_code, 200)
        session_token = self.client.cookies.get(SESSION_COOKIE_NAME)
        self.assertTrue(session_token)
        self.assertTrue(self.client.get("/api/v1/auth/me").json()["data"]["authenticated"])
        self.assertEqual(self.client.get("/api/v1/settings").status_code, 200)

        self.assertEqual(self.client.post("/api/v1/auth/logout").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/settings").status_code, 401)
        self.client.cookies.set(SESSION_COOKIE_NAME, session_token)
        replay = self.client.get("/api/v1/settings")
        self.assertEqual(replay.status_code, 401)

    def test_login_is_rate_limited_after_repeated_bad_passwords(self):
        for _ in range(5):
            self.assertEqual(
                self.client.post("/api/v1/auth/login", json={"password": "wrong"}).status_code,
                401,
            )
        limited = self.client.post(
            "/api/v1/auth/login",
            json={"password": "correct horse battery staple"},
        )
        self.assertEqual(limited.status_code, 429)
        self.assertTrue(limited.headers["retry-after"])


if __name__ == "__main__":
    unittest.main()
