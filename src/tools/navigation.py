# navigation tools - navigate, back, forward, reload, page info
from typing import Any

from src.response import ToolResponse
from src.tools.base import ToolBase


class NavigationTools(ToolBase):
    """tools for page navigation"""

    def _register_tools(self) -> None:
        """register navigation tools"""
        self._register(self.navigate)
        self._register(self.go_back)
        self._register(self.go_forward)
        self._register(self.reload_page)
        self._register(self.get_page_info)

    async def navigate(self, url: str) -> str:
        """Navigate to a URL."""
        await self.session.navigate(url)
        return f"Navigated to {url}"

    async def go_back(self) -> str:
        """Navigate back in browser history."""
        await self.session.page.back()
        return "Navigated back"

    async def go_forward(self) -> str:
        """Navigate forward in browser history."""
        await self.session.page.forward()
        return "Navigated forward"

    async def reload_page(self) -> str:
        """Reload the current page."""
        await self.session.page.reload()
        return "Page reloaded"

    async def get_page_info(self) -> dict[str, Any]:
        """Return the current tab's URL and title."""
        page = self.session.page
        url = getattr(page, "url", "unknown")
        title = getattr(page, "title", "unknown")
        return ToolResponse(
            summary=f"{title} - {url}",
            data={"url": url, "title": title},
        ).to_dict()
