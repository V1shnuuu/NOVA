"""Tests for window_manager.py — keyword matching logic."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from automation.window_manager import WindowManager, _WINDOW_KEYWORDS


class TestWindowKeywords(unittest.TestCase):
    """Verify the keyword dictionary covers all expected apps."""

    def test_chatgpt_keywords(self) -> None:
        self.assertIn("ChatGPT", _WINDOW_KEYWORDS["chatgpt"])

    def test_claude_keywords(self) -> None:
        self.assertIn("Claude", _WINDOW_KEYWORDS["claude"])

    def test_spotify_keywords(self) -> None:
        self.assertIn("Spotify", _WINDOW_KEYWORDS["spotify"])


class TestWindowManager(unittest.TestCase):
    """Verify WindowManager construction and screen size retrieval."""

    @patch("automation.window_manager.ctypes")
    def test_screen_size(self, mock_ctypes: MagicMock) -> None:
        mock_user32 = MagicMock()
        mock_user32.GetSystemMetrics.side_effect = [1920, 1080]
        mock_ctypes.windll.user32 = mock_user32

        config = MagicMock()
        config.layout = {"chatgpt": {"x": 0, "y": 0, "w": 0.33, "h": 1.0}}
        config.window_find_timeout = 10

        mgr = WindowManager(config)
        self.assertEqual(mgr.screen_width, 1920)
        self.assertEqual(mgr.screen_height, 1080)


if __name__ == "__main__":
    unittest.main()
