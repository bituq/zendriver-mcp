"""Tests for the CLI argument parser."""

from __future__ import annotations

import pytest

from src.server import _parse_args


def test_defaults() -> None:
    ns = _parse_args([])
    assert ns.browser_path is None
    assert ns.transport == "stdio"


def test_browser_path_passthrough() -> None:
    ns = _parse_args(["--browser-path", "/opt/chrome"])
    assert ns.browser_path == "/opt/chrome"


def test_rejects_unknown_transport() -> None:
    with pytest.raises(SystemExit):
        _parse_args(["--transport", "websocket"])
