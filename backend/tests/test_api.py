import unittest
import os
import sys
from unittest.mock import patch
from starlette.requests import Request

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.main import root_info
from backend.app.core.db import db
from backend.app.api.v1.health import health_check, get_system_resources
from backend.app.api.v1.settings import get_ai_provider_status, get_settings, update_settings
from backend.app.api.v1.auth import get_current_user_status
from backend.app.models.schemas import UserSettingsUpdate

class TestBackendFoundationDirect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()

    def test_root_endpoint(self):
        data = root_info()
        self.assertEqual(data["status"], "online")
        self.assertIn("version", data)
        self.assertIn("health", data)

    def test_system_resources(self):
        resources = get_system_resources()
        self.assertGreater(resources.cpu_cores, 0)
        self.assertGreater(resources.total_ram_gb, 0)
        self.assertGreater(resources.free_disk_gb, 0)
        self.assertEqual(resources.os_name, "Windows")

    def test_health_endpoint(self):
        response = health_check()
        self.assertTrue(response.success)
        data = response.data
        self.assertIn(data.status, ["healthy", "degraded"])
        self.assertIn("sqlite", data.database)
        self.assertGreater(data.resources.cpu_cores, 0)

    def test_get_settings(self):
        response = get_settings()
        self.assertTrue(response.success)
        data = response.data
        self.assertIn(data.theme, ["dark", "light", "system"])
        self.assertGreaterEqual(data.reminder_interval_mins, 1)

    def test_ai_provider_status_reports_configuration_without_exposing_keys(self):
        with patch("backend.app.api.v1.settings.app_settings.GEMINI_API_KEY", "gemini-secret"), patch(
            "backend.app.api.v1.settings.app_settings.GROQ_API_KEY", ""
        ):
            response = get_ai_provider_status()

        self.assertTrue(response.success)
        self.assertTrue(response.data.gemini_configured)
        self.assertFalse(response.data.groq_configured)
        self.assertNotIn("gemini-secret", response.model_dump_json())

    def test_update_settings(self):
        # Update theme to light and reminder interval to 30
        update_req = UserSettingsUpdate(theme="light", reminder_interval_mins=30)
        patch_response = update_settings(update_req)
        self.assertTrue(patch_response.success)
        data = patch_response.data
        self.assertEqual(data.theme, "light")
        self.assertEqual(data.reminder_interval_mins, 30)

        # Restore back to dark and 15
        restore_req = UserSettingsUpdate(theme="dark", reminder_interval_mins=15)
        restore_response = update_settings(restore_req)
        self.assertTrue(restore_response.success)
        self.assertEqual(restore_response.data.theme, "dark")
        self.assertEqual(restore_response.data.reminder_interval_mins, 15)

    def test_auth_me_endpoint(self):
        request = Request({"type": "http", "headers": []})
        response = get_current_user_status(request)
        self.assertTrue(response.success)
        data = response.data
        self.assertTrue(data.authenticated)
        self.assertIsNotNone(data.profile)
        self.assertIsNotNone(data.settings)
        self.assertEqual(data.email, "developer@local.host")

if __name__ == "__main__":
    unittest.main()
