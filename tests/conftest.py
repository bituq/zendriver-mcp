"""Shared pytest fixtures for the zendriver-mcp test suite.

The MCP server's ``BrowserSession`` is a module-level singleton that
survives across test cases. Without an autouse teardown, one test's
reset callbacks, network log buffer, or cached ``_page`` leak into the
next test and cause spurious failures.

``reset_browser_session`` runs automatically for every test, nulling the
singleton + re-creating empty state. Tests that want sharper control
can still depend on the explicit ``fresh_session`` fixture directly.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from src.session import BrowserSession


@pytest.fixture(autouse=True)
def reset_browser_session() -> None:
    """Null the BrowserSession singleton before every test."""
    BrowserSession._instance = None


@pytest.fixture
def fresh_session() -> BrowserSession:
    """Explicit handle on a freshly-constructed session."""
    BrowserSession._instance = None
    return BrowserSession.get_instance()


@pytest.fixture
def stub_mcp() -> Any:
    """Minimal FastMCP stand-in that records registered tools."""
    mcp = MagicMock()
    mcp.tool.return_value = lambda fn: fn
    return mcp
