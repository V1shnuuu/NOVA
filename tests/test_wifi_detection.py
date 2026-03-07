"""Tests for wifi_presence.py — ping and ARP detection strategies."""

from __future__ import annotations

import unittest
from unittest.mock import patch, MagicMock

from triggers.wifi_presence import ping_device, arp_scan


class TestPingDevice(unittest.TestCase):
    """Verify the ping detection helper."""

    @patch("triggers.wifi_presence.subprocess.run")
    def test_ping_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="Reply from 10.0.0.1: bytes=32 TTL=64")
        self.assertTrue(ping_device("10.0.0.1"))

    @patch("triggers.wifi_presence.subprocess.run")
    def test_ping_failure(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="Request timed out.")
        self.assertFalse(ping_device("10.0.0.1"))

    @patch("triggers.wifi_presence.subprocess.run", side_effect=FileNotFoundError)
    def test_ping_command_missing(self, _mock: MagicMock) -> None:
        self.assertFalse(ping_device("10.0.0.1"))


class TestArpScan(unittest.TestCase):
    """Verify the ARP detection helper."""

    @patch("triggers.wifi_presence.subprocess.run")
    def test_arp_found(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            stdout="  10.0.0.42   aa-bb-cc-dd-ee-ff   dynamic\n"
        )
        self.assertTrue(arp_scan("AA:BB:CC:DD:EE:FF"))

    @patch("triggers.wifi_presence.subprocess.run")
    def test_arp_not_found(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="  10.0.0.1   11-22-33-44-55-66   dynamic\n")
        self.assertFalse(arp_scan("AA:BB:CC:DD:EE:FF"))


if __name__ == "__main__":
    unittest.main()
