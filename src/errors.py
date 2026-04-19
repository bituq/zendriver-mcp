"""Typed exceptions raised by Zendriver MCP tools."""

from __future__ import annotations


class ZendriverMCPError(Exception):
    """Base class for all Zendriver MCP tool errors."""


class BrowserNotStartedError(ZendriverMCPError):
    """Raised when a tool is called before ``start_browser``."""

    def __init__(self, message: str = "Browser not started. Call start_browser first.") -> None:
        super().__init__(message)


class PageNotLoadedError(ZendriverMCPError):
    """Raised when a tool expects a loaded tab but the session has none."""

    def __init__(self, message: str = "No page loaded. Navigate to a URL first.") -> None:
        super().__init__(message)


class ElementNotFoundError(ZendriverMCPError):
    """Raised when a selector/text lookup yields nothing."""

    def __init__(self, selector: str) -> None:
        super().__init__(f"Element not found: {selector}")
        self.selector = selector


class CloudflareChallengeError(ZendriverMCPError):
    """Raised when a Cloudflare challenge cannot be solved within the timeout."""


class TracingError(ZendriverMCPError):
    """Raised on unexpected state transitions around Tracing.* commands."""


class LighthouseNotInstalledError(ZendriverMCPError):
    """Raised when ``lighthouse`` CLI is missing on the PATH."""

    def __init__(self) -> None:
        super().__init__("Lighthouse CLI not found. Install with `npm i -g lighthouse`.")


class AccessibilityUidError(ZendriverMCPError):
    """Raised when a caller references an unknown or stale accessibility uid."""


class ToolTimeoutError(ZendriverMCPError):
    """Raised when a tool exceeds its time budget.

    Prevents a single hung CDP command from freezing the whole MCP session.
    Override the default via the ``ZENDRIVER_MCP_TOOL_TIMEOUT`` env var or the
    per-tool ``timeout`` argument at registration.
    """

    def __init__(self, tool: str, seconds: float) -> None:
        super().__init__(f"Tool {tool!r} timed out after {seconds:.1f}s")
        self.tool = tool
        self.seconds = seconds
