"""Ensure ``get_accessibility_snapshot`` hands out stable uids across calls."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.session import BrowserSession
from src.tools.accessibility import AccessibilityTools


def _single_button_tree(backend_id: int) -> list[dict[str, Any]]:
    return [
        {
            "nodeId": "1",
            "parentId": None,
            "ignored": False,
            "role": {"type": "role", "value": "RootWebArea"},
            "name": {"type": "computedString", "value": "Page"},
            "childIds": ["2"],
            "backendDOMNodeId": 999,
        },
        {
            "nodeId": "2",
            "parentId": "1",
            "ignored": False,
            "role": {"type": "role", "value": "button"},
            "name": {"type": "computedString", "value": "Click me"},
            "childIds": [],
            "backendDOMNodeId": backend_id,
        },
    ]


@pytest.fixture
def ax_tools() -> AccessibilityTools:
    BrowserSession._instance = None
    mcp = MagicMock()
    mcp.tool.return_value = lambda fn: fn
    return AccessibilityTools(mcp)


async def _run(tools: AccessibilityTools, raw: list[dict[str, Any]]) -> dict[str, Any]:
    fake_tab = MagicMock()
    fake_tab.send = AsyncMock(side_effect=[None, raw])
    tools.session._page = fake_tab  # type: ignore[attr-defined]
    return await tools.get_accessibility_snapshot()


async def test_button_uid_reused_across_snapshots(ax_tools: AccessibilityTools) -> None:
    first = await _run(ax_tools, _single_button_tree(backend_id=42))
    second = await _run(ax_tools, _single_button_tree(backend_id=42))

    def find_button(tree: dict[str, Any]) -> dict[str, Any]:
        if tree.get("role") == "button":
            return tree
        for child in tree.get("children", []):
            hit = find_button(child)
            if hit:
                return hit
        return {}

    button_a = find_button(first["data"]["tree"])
    button_b = find_button(second["data"]["tree"])
    assert button_a
    assert button_b
    assert button_a["uid"] == button_b["uid"], "backend_node_id stayed the same, uid should too"


async def test_different_backend_id_gets_different_uid(
    ax_tools: AccessibilityTools,
) -> None:
    first = await _run(ax_tools, _single_button_tree(backend_id=100))
    second = await _run(ax_tools, _single_button_tree(backend_id=200))

    def find_button(tree: dict[str, Any]) -> dict[str, Any]:
        if tree.get("role") == "button":
            return tree
        for child in tree.get("children", []):
            hit = find_button(child)
            if hit:
                return hit
        return {}

    assert find_button(first["data"]["tree"])["uid"] != find_button(second["data"]["tree"])["uid"]
