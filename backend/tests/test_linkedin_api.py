import os
import sqlite3
import tempfile
import unittest
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
import httpx

from backend.app.core.config import settings
from backend.app.core.db import DEFAULT_USER_ID, db
from backend.app.main import app
from backend.app.api.v1.linkedin import _connection, _connection_token


class TestLinkedInOAuthAndPublishing(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = db.db_path
        db.db_path = os.path.join(self.temp_dir.name, "linkedin-test.db")
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
        self.key = Fernet.generate_key().decode("ascii")
        self.settings_patch = patch.multiple(
            settings,
            LINKEDIN_CLIENT_ID="test-client",
            LINKEDIN_CLIENT_SECRET="test-secret",
            LINKEDIN_TOKEN_ENCRYPTION_KEY=self.key,
            LINKEDIN_REDIRECT_URI="http://testserver/api/v1/linkedin/callback",
            LINKEDIN_FRONTEND_URL="http://testserver",
            LINKEDIN_API_VERSION="202611",
            ENABLE_BACKGROUND_SCHEDULER=False,
        )
        self.settings_patch.start()
        self.client_context = TestClient(app, follow_redirects=False)
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        self.settings_patch.stop()
        db.db_path = self.original_db_path
        self.temp_dir.cleanup()

    def test_oauth_state_token_encryption_and_member_post(self):
        connect = self.client.get("/api/v1/linkedin/connect")
        self.assertEqual(connect.status_code, 303)
        query = parse_qs(urlparse(connect.headers["location"]).query)
        self.assertEqual(query["scope"], ["openid profile w_member_social"])
        state = query["state"][0]

        with patch(
            "backend.app.api.v1.linkedin.httpx.post",
            return_value=httpx.Response(200, json={"access_token": "secret-token", "expires_in": 3600}),
        ) as exchange, patch(
            "backend.app.api.v1.linkedin.httpx.get",
            return_value=httpx.Response(200, json={"sub": "member-123", "name": "Tilak C"}),
        ):
            callback = self.client.get(
                "/api/v1/linkedin/callback",
                params={"code": "oauth-code", "state": state},
            )
        self.assertEqual(callback.status_code, 303)
        self.assertTrue(callback.headers["location"].endswith("/?linkedin=connected"))
        exchange.assert_called_once()

        stored_connection = _connection()
        self.assertIsNotNone(stored_connection)
        self.assertNotIn("secret-token", stored_connection["encrypted_token"])
        self.assertEqual(_connection_token(stored_connection), "secret-token")
        self.assertEqual(stored_connection["person_urn"], "urn:li:person:member-123")
        self.assertEqual(stored_connection["member_name"], "Tilak C")

        with patch(
            "backend.app.api.v1.linkedin.httpx.post",
            return_value=httpx.Response(201, headers={"x-restli-id": "urn:li:share:post-1"}),
        ) as publish:
            from backend.app.api.v1.linkedin import publish_linkedin_post

            post_id = publish_linkedin_post("Approved post text")
        self.assertEqual(post_id, "urn:li:share:post-1")
        request = publish.call_args
        self.assertEqual(request.kwargs["headers"]["Linkedin-Version"], "202611")
        self.assertEqual(request.kwargs["headers"]["X-Restli-Protocol-Version"], "2.0.0")
        self.assertEqual(request.kwargs["json"]["author"], "urn:li:person:member-123")
        self.assertEqual(request.kwargs["json"]["commentary"], "Approved post text")

        replay = self.client.get(
            "/api/v1/linkedin/callback",
            params={"code": "replayed-code", "state": state},
        )
        self.assertEqual(replay.status_code, 400)


if __name__ == "__main__":
    unittest.main()
