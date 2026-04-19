"""Accessibility tree with stable uids.

The DOM walker upstream returns numeric IDs based on DOM traversal order;
they re-number on every tree mutation. For long interactive agent flows
we also expose the CDP accessibility tree keyed by stable uids that stay
valid as long as the underlying backend node still exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from mcp.server.fastmcp import FastMCP
from zendriver import cdp

from src.errors import AccessibilityUidError, ElementNotFoundError
from src.response import ToolResponse
from src.tools.base import ToolBase


@dataclass(slots=True)
class _UidEntry:
    backend_node_id: int
    role: str
    name: str


class AccessibilityTools(ToolBase):
    """Accessibility-tree snapshots with stable, re-usable uids."""

    def __init__(self, mcp: FastMCP) -> None:
        super().__init__(mcp)
        # Uid -> metadata. Lives for the session; entries become stale if the
        # underlying backend node is removed from the DOM.
        self._uids: dict[str, _UidEntry] = {}

    def _register_tools(self) -> None:
        self._mcp.tool()(self.get_accessibility_snapshot)
        self._mcp.tool()(self.click_by_uid)
        self._mcp.tool()(self.describe_uid)

    async def get_accessibility_snapshot(
        self, max_nodes: int = 400, interesting_only: bool = True
    ) -> dict[str, Any]:
        """Return the page's accessibility tree with stable uids.

        Each node looks like ``{"uid": "ax_1b2c", "role": "button",
        "name": "Submit", "children": [...]}``. The uid can be passed to
        ``click_by_uid`` for deterministic interaction.

        - ``max_nodes``: cap the node count to keep the response small.
        - ``interesting_only``: drop nodes with empty role+name and no
          interactive properties.
        """
        tab = self.session.page
        await tab.send(cdp.accessibility.enable())
        nodes = await tab.send(cdp.accessibility.get_full_ax_tree())

        self._uids.clear()
        by_id: dict[str, cdp.accessibility.AXNode] = {str(n.node_id): n for n in nodes}

        interactive_roles = {
            "button",
            "link",
            "textbox",
            "searchbox",
            "checkbox",
            "radio",
            "switch",
            "combobox",
            "menuitem",
            "tab",
            "option",
        }

        def render(node: cdp.accessibility.AXNode) -> dict[str, Any] | None:
            if len(self._uids) >= max_nodes:
                return None
            role = str(node.role.value) if node.role and node.role.value else ""
            name = str(node.name.value) if node.name and node.name.value else ""
            if interesting_only and not role and not name:
                children_rendered: list[dict[str, Any]] = []
                for cid in node.child_ids or []:
                    child = by_id.get(str(cid))
                    if child is None:
                        continue
                    r = render(child)
                    if r is not None:
                        children_rendered.append(r)
                # Collapse: return children directly (skip invisible wrapper).
                return (
                    {"uid": "", "role": "", "name": "", "children": children_rendered}
                    if children_rendered
                    else None
                )

            if node.ignored and role not in interactive_roles:
                return None

            uid = f"ax_{uuid4().hex[:8]}"
            self._uids[uid] = _UidEntry(
                backend_node_id=int(node.backend_dom_node_id)
                if node.backend_dom_node_id is not None
                else 0,
                role=role,
                name=name,
            )
            rendered: dict[str, Any] = {"uid": uid, "role": role, "name": name}
            children: list[dict[str, Any]] = []
            for cid in node.child_ids or []:
                child = by_id.get(str(cid))
                if child is None:
                    continue
                r = render(child)
                if r is not None:
                    children.append(r)
            if children:
                rendered["children"] = children
            return rendered

        if not nodes:
            return ToolResponse(summary="Empty accessibility tree", data={"nodes": []}).to_dict()
        root = render(nodes[0]) or {}
        return ToolResponse(
            summary=f"Accessibility snapshot: {len(self._uids)} nodes",
            data={"tree": root, "uid_count": len(self._uids)},
        ).to_dict()

    async def describe_uid(self, uid: str) -> dict[str, Any]:
        """Return the cached role + name for a uid, or raise if unknown."""
        entry = self._uids.get(uid)
        if entry is None:
            raise AccessibilityUidError(f"Unknown accessibility uid: {uid}")
        return {
            "uid": uid,
            "role": entry.role,
            "name": entry.name,
            "backend_node_id": entry.backend_node_id,
        }

    async def click_by_uid(self, uid: str) -> str:
        """Click the DOM node behind an accessibility uid.

        Resolves the cached ``backend_node_id`` to a remote object, then
        dispatches a native element click. Raises ``AccessibilityUidError``
        if the uid is unknown or the node was removed since the snapshot.
        """
        entry = self._uids.get(uid)
        if entry is None or entry.backend_node_id == 0:
            raise AccessibilityUidError(f"Unknown or non-DOM uid: {uid}")

        tab = self.session.page
        try:
            remote = await tab.send(
                cdp.dom.resolve_node(backend_node_id=cdp.dom.BackendNodeId(entry.backend_node_id))
            )
        except Exception as exc:  # zendriver raises ProtocolException on stale nodes
            raise AccessibilityUidError(f"uid {uid} no longer maps to a live DOM node") from exc

        if remote is None or remote.object_id is None:
            raise ElementNotFoundError(f"uid:{uid}")

        # Scroll into view + get center, then native click via Input.dispatchMouseEvent.
        quads = await tab.send(cdp.dom.get_content_quads(object_id=remote.object_id))
        if not quads:
            raise AccessibilityUidError(f"uid {uid} has no visible content box")
        # First quad = [x1, y1, x2, y2, x3, y3, x4, y4]
        q = quads[0]
        cx = (q[0] + q[2] + q[4] + q[6]) / 4
        cy = (q[1] + q[3] + q[5] + q[7]) / 4
        await tab.send(
            cdp.input_.dispatch_mouse_event(
                type_="mousePressed",
                x=cx,
                y=cy,
                button=cdp.input_.MouseButton.LEFT,
                click_count=1,
            )
        )
        await tab.send(
            cdp.input_.dispatch_mouse_event(
                type_="mouseReleased",
                x=cx,
                y=cy,
                button=cdp.input_.MouseButton.LEFT,
                click_count=1,
            )
        )
        return f"Clicked uid {uid} ({entry.role}: {entry.name[:40]})"
