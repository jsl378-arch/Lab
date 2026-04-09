"""Tests for send_message.py"""

import importlib
import json
import os
import sys
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_module():
    """Import (or re-import) send_message so each test gets a clean slate."""
    if "send_message" in sys.modules:
        del sys.modules["send_message"]
    import send_message  # noqa: PLC0415
    return send_message


class TestGetMessage(unittest.TestCase):
    def test_default_message_contains_good_evening(self):
        mod = _load_module()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("EVENING_MESSAGE", None)
            msg = mod.get_message()
        self.assertIn("Good evening", msg)

    def test_custom_message_from_env(self):
        mod = _load_module()
        with patch.dict(os.environ, {"EVENING_MESSAGE": "Hello from test!"}):
            msg = mod.get_message()
        self.assertEqual(msg, "Hello from test!")


class TestSendSlack(unittest.TestCase):
    def _make_response(self, status: int = 200):
        resp = MagicMock()
        resp.status = status
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        return resp

    def test_posts_to_webhook(self):
        mod = _load_module()
        webhook = "https://hooks.slack.com/test"
        env = {"SLACK_WEBHOOK_URL": webhook}
        with patch.dict(os.environ, env):
            with patch("urllib.request.urlopen", return_value=self._make_response()) as mock_open:
                mod.send_slack("Hi Slack!")
        mock_open.assert_called_once()
        req = mock_open.call_args[0][0]
        self.assertEqual(req.full_url, webhook)
        self.assertEqual(json.loads(req.data), {"text": "Hi Slack!"})

    def test_raises_on_non_200(self):
        mod = _load_module()
        env = {"SLACK_WEBHOOK_URL": "https://hooks.slack.com/test"}
        with patch.dict(os.environ, env):
            with patch("urllib.request.urlopen", return_value=self._make_response(500)):
                with self.assertRaises(RuntimeError):
                    mod.send_slack("oops")


class TestSendDiscord(unittest.TestCase):
    def _make_response(self, status: int = 204):
        resp = MagicMock()
        resp.status = status
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        return resp

    def test_posts_to_webhook(self):
        mod = _load_module()
        webhook = "https://discord.com/api/webhooks/test"
        env = {"DISCORD_WEBHOOK_URL": webhook}
        with patch.dict(os.environ, env):
            with patch("urllib.request.urlopen", return_value=self._make_response()) as mock_open:
                mod.send_discord("Hi Discord!")
        mock_open.assert_called_once()
        req = mock_open.call_args[0][0]
        self.assertEqual(req.full_url, webhook)
        self.assertEqual(json.loads(req.data), {"content": "Hi Discord!"})

    def test_raises_on_error_status(self):
        mod = _load_module()
        env = {"DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/test"}
        with patch.dict(os.environ, env):
            with patch("urllib.request.urlopen", return_value=self._make_response(500)):
                with self.assertRaises(RuntimeError):
                    mod.send_discord("oops")


class TestSendEmail(unittest.TestCase):
    def test_sends_email(self):
        mod = _load_module()
        env = {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "user@example.com",
            "SMTP_PASSWORD": "secret",
            "EMAIL_RECIPIENT": "recipient@example.com",
            "EMAIL_SUBJECT": "Test",
        }
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = lambda s: s
        mock_smtp.__exit__ = MagicMock(return_value=False)
        with patch.dict(os.environ, env):
            with patch("smtplib.SMTP", return_value=mock_smtp):
                mod.send_email("Hello by email")
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("user@example.com", "secret")
        mock_smtp.sendmail.assert_called_once()


class TestMain(unittest.TestCase):
    def test_invalid_channel_exits(self):
        mod = _load_module()
        with patch.dict(os.environ, {"MESSAGE_CHANNEL": "carrier_pigeon"}):
            with self.assertRaises(SystemExit) as ctx:
                mod.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_main_calls_correct_channel(self):
        mod = _load_module()
        mock_send = MagicMock()
        with patch.dict(os.environ, {"MESSAGE_CHANNEL": "slack", "SLACK_WEBHOOK_URL": "https://hooks.slack.com/x"}):
            with patch.dict(mod.CHANNELS, {"slack": mock_send}):
                mod.main()
        mock_send.assert_called_once()


if __name__ == "__main__":
    unittest.main()
