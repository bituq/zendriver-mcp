"""Smoke tests that verify the MCP server imports and registers tools correctly."""

from __future__ import annotations

from src.tools import mcp


def test_mcp_server_initialises() -> None:
    assert mcp is not None


def test_expected_tool_count() -> None:
    # Guards against accidental tool removal; bump when we deliberately add tools.
    tools = mcp._tool_manager._tools
    assert len(tools) >= 59, f"expected at least 59 tools registered, got {len(tools)}"


def test_core_tools_registered() -> None:
    tools = mcp._tool_manager._tools
    must_have = {
        "start_browser",
        "stop_browser",
        "navigate",
        "click",
        "type_text",
        "get_interaction_tree",
        "screenshot",
        "get_network_logs",
        "get_console_logs",
        "bypass_cloudflare",
        "set_user_agent",
        "set_locale",
        "set_timezone",
        "set_geolocation",
        "human_click",
        "human_type",
    }
    missing = must_have - tools.keys()
    assert not missing, f"missing core tools: {missing}"
