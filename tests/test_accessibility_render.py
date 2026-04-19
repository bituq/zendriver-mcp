"""Unit tests for the accessibility tree rendering logic.

These don't need a browser - we feed synthetic raw AX node dicts through
the snapshot pipeline and assert the rendered tree matches expectations.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.session import BrowserSession
from src.tools.accessibility import AccessibilityTools


def _example_dot_com_ax_tree() -> list[dict[str, Any]]:
    """Representative fixture based on real Chrome output for example.com."""
    return [
        {
            "nodeId": "2",
            "parentId": None,
            "ignored": False,
            "role": {"type": "role", "value": "RootWebArea"},
            "name": {"type": "computedString", "value": "Example Domain"},
            "childIds": ["3"],
            "backendDOMNodeId": 100,
        },
        {
            "nodeId": "3",
            "parentId": "2",
            "ignored": True,
            "role": {"type": "role", "value": "none"},
            "childIds": ["10", "12"],
            "backendDOMNodeId": 101,
        },
        {
            "nodeId": "10",
            "parentId": "3",
            "ignored": False,
            "role": {"type": "role", "value": "heading"},
            "name": {"type": "computedString", "value": "Example Domain"},
            "childIds": ["11"],
            "backendDOMNodeId": 110,
        },
        {
            "nodeId": "11",
            "parentId": "10",
            "ignored": False,
            "role": {"type": "role", "value": "StaticText"},
            "name": {"type": "computedString", "value": "Example Domain"},
            "childIds": [],
        },
        {
            "nodeId": "12",
            "parentId": "3",
            "ignored": False,
            "role": {"type": "role", "value": "link"},
            "name": {"type": "computedString", "value": "Learn more"},
            "childIds": [],
            "backendDOMNodeId": 120,
        },
    ]


async def _run_snapshot(
    tools: AccessibilityTools, raw: list[dict[str, Any]], **kwargs: Any
) -> dict[str, Any]:
    fake_tab = MagicMock()
    fake_tab.send = AsyncMock(side_effect=[None, raw])
    tools.session._page = fake_tab  # type: ignore[attr-defined]
    return await tools.get_accessibility_snapshot(**kwargs)


@pytest.fixture
def ax_tools() -> AccessibilityTools:
    mcp = MagicMock()
    mcp.tool.return_value = lambda fn: fn
    BrowserSession._instance = None  # isolated session per test
    return AccessibilityTools(mcp)


async def test_interesting_only_keeps_headings_and_links(
    ax_tools: AccessibilityTools,
) -> None:
    result = await _run_snapshot(ax_tools, _example_dot_com_ax_tree())
    tree = result["data"]["tree"]

    # Root survives, children are the heading + link (StaticText collapsed).
    assert tree["role"] == "RootWebArea"
    assert {c["role"] for c in tree["children"]} == {"heading", "link"}
    # StaticText is filtered; heading has no rendered children.
    heading = next(c for c in tree["children"] if c["role"] == "heading")
    assert "children" not in heading or not heading["children"]


async def test_noise_nodes_are_skipped_but_children_bubble_up(
    ax_tools: AccessibilityTools,
) -> None:
    # The "none"/ignored=true wrapper (id=3) must not become its own node.
    result = await _run_snapshot(ax_tools, _example_dot_com_ax_tree())
    tree = result["data"]["tree"]
    roles_in_tree = [tree["role"]] + [c["role"] for c in tree.get("children", [])]
    assert "none" not in roles_in_tree


async def test_max_nodes_caps_output(ax_tools: AccessibilityTools) -> None:
    result = await _run_snapshot(ax_tools, _example_dot_com_ax_tree(), max_nodes=1)
    assert result["data"]["uid_count"] == 1


async def test_uids_are_registered_with_backend_ids(
    ax_tools: AccessibilityTools,
) -> None:
    result = await _run_snapshot(ax_tools, _example_dot_com_ax_tree())
    # Every uid in the rendered tree must be in _uids.
    uids: list[str] = []

    def collect(node: dict[str, Any]) -> None:
        if node.get("uid"):
            uids.append(node["uid"])
        for c in node.get("children", []):
            collect(c)

    collect(result["data"]["tree"])
    assert uids  # non-empty
    for uid in uids:
        assert uid in ax_tools._uids
        assert ax_tools._uids[uid].backend_node_id >= 0


def test_snapshot_result_shape_sync_sanity() -> None:
    """Not strictly async; just keeps the contract visible to reviewers."""
    assert asyncio.iscoroutinefunction(AccessibilityTools.get_accessibility_snapshot)
