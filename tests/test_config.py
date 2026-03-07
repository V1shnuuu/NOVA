"""Tests for config.py — JSON persistence and default values."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from config import Config


class TestConfig(unittest.TestCase):
    """Verify Config load/save round-trip and resilience."""

    def test_defaults(self) -> None:
        c = Config()
        self.assertTrue(c.first_run)
        self.assertFalse(c.setup_complete)
        self.assertEqual(c.hotkey, "ctrl+alt+w")
        self.assertEqual(c.spotify_volume, 40)

    def test_save_and_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_file = Path(tmp) / "config.json"
            with patch("config.CONFIG_FILE", tmp_file), \
                 patch("config.CONFIG_DIR", Path(tmp)):
                c = Config(phone_ip="10.0.0.42", hotkey="ctrl+shift+j")
                c.save()
                loaded = Config.load()
                self.assertEqual(loaded.phone_ip, "10.0.0.42")
                self.assertEqual(loaded.hotkey, "ctrl+shift+j")

    def test_load_corrupt_file_returns_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_file = Path(tmp) / "config.json"
            tmp_file.write_text("NOT VALID JSON!!!", encoding="utf-8")
            with patch("config.CONFIG_FILE", tmp_file), \
                 patch("config.CONFIG_DIR", Path(tmp)):
                c = Config.load()
                self.assertTrue(c.first_run)

    def test_load_missing_file_returns_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch("config.CONFIG_FILE", Path(tmp) / "nope.json"), \
                 patch("config.CONFIG_DIR", Path(tmp)):
                c = Config.load()
                self.assertTrue(c.first_run)

    def test_layout_default_has_three_apps(self) -> None:
        c = Config()
        self.assertIn("chatgpt", c.layout)
        self.assertIn("claude", c.layout)
        self.assertIn("spotify", c.layout)


if __name__ == "__main__":
    unittest.main()
