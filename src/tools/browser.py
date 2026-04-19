# browser lifecycle tools - start, stop, status

from typing import Any

from src.response import ToolResponse
from src.tools.base import ToolBase


class BrowserTools(ToolBase):
    """tools for browser lifecycle management"""

    def _register_tools(self) -> None:
        """register browser lifecycle tools"""
        # Cold Chrome launch can take a few seconds on first run.
        self._register(self.start_browser, timeout=120)
        self._register(self.stop_browser, timeout=30)
        self._register(self.get_browser_status)

    async def start_browser(
        self, headless: bool = False, proxy: str | None = None, user_data_dir: str | None = None
    ) -> str:
        """Start the browser with configuration options."""
        await self.session.start(headless=headless, proxy=proxy, user_data_dir=user_data_dir)
        mode = "headless" if headless else "headed"
        extras = []
        if proxy:
            extras.append(f"proxy={proxy}")
        if user_data_dir:
            extras.append(f"profile={user_data_dir}")
        extra_info = f" ({', '.join(extras)})" if extras else ""
        return f"Browser started in {mode} mode{extra_info}"

    async def stop_browser(self) -> str:
        """Stop the browser and clean up all resources."""
        await self.session.stop()
        return "Browser stopped and all resources cleaned up"

    async def get_browser_status(self) -> dict[str, Any]:
        """Return browser running state plus a list of open tabs."""
        if not self.session.is_browser_started():
            return ToolResponse(summary="Browser: Not started", data={"running": False}).to_dict()

        tabs = self.session.get_all_tabs()
        return ToolResponse(
            summary=f"Browser running with {len(tabs)} tab(s)",
            data={
                "running": True,
                "tab_count": len(tabs),
                "tabs": [{"id": tid, "url": url} for tid, url in tabs.items()],
            },
        ).to_dict()
