# tab management tools - new tab, list, switch, close

from typing import Any

from src.response import ToolResponse
from src.tools.base import ToolBase


class TabTools(ToolBase):
    """tools for multi-tab management"""

    def _register_tools(self) -> None:
        """register tab management tools"""
        self._register(self.new_tab)
        self._register(self.list_tabs)
        self._register(self.switch_tab)
        self._register(self.close_tab)

    async def new_tab(self, url: str | None = None) -> str:
        """Open a new browser tab."""
        tab_id, tab = await self.session.create_tab(url)
        self.session.page = tab
        return f"Opened new tab: {tab_id}" + (f" at {url}" if url else "")

    async def list_tabs(self) -> dict[str, Any]:
        """List all open tabs with their URLs."""
        tabs = self.session.get_all_tabs()
        return ToolResponse(
            summary=f"{len(tabs)} tab(s) open",
            data={
                "count": len(tabs),
                "tabs": [{"id": tid, "url": url} for tid, url in tabs.items()],
            },
        ).to_dict()

    async def switch_tab(self, tab_id: str) -> str:
        """Switch to a specific tab."""
        await self.session.switch_tab(tab_id)
        return f"Switched to {tab_id}"

    async def close_tab(self, tab_id: str) -> str:
        """Close a specific tab."""
        await self.session.close_tab(tab_id)
        return f"Closed tab: {tab_id}"
