"""Screencast: CDP-driven frame capture to disk.

Uses ``Page.startScreencast`` which emits ``screencastFrame`` events with
base64-encoded JPEG/PNG data. We write each frame to a directory and ack the
frame so Chrome keeps sending new ones.
"""

from __future__ import annotations

import asyncio
import base64
import tempfile
from collections.abc import Awaitable, Callable
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from zendriver import cdp

from src.errors import ZendriverMCPError
from src.response import ToolResponse
from src.tools.base import ToolBase

FrameHandler = Callable[[cdp.page.ScreencastFrame], Awaitable[None]]


class ScreencastTools(ToolBase):
    """Start/stop a screencast recording into a directory of frames."""

    def __init__(self, mcp: FastMCP) -> None:
        super().__init__(mcp)
        self._frame_dir: Path | None = None
        self._frame_count = 0
        self._frame_format = "jpeg"
        self._handler: FrameHandler | None = None

    def _register_tools(self) -> None:
        self._mcp.tool()(self.start_screencast)
        self._mcp.tool()(self.stop_screencast)

    async def start_screencast(
        self,
        output_dir: str = "",
        fmt: str = "jpeg",
        quality: int = 80,
        max_width: int = 1280,
        every_nth_frame: int = 1,
    ) -> dict[str, object]:
        """Begin recording screencast frames to ``output_dir``.

        - ``fmt``: ``"jpeg"`` (smaller) or ``"png"`` (lossless).
        - ``quality``: 0-100, JPEG only.
        - ``max_width``: frames are downscaled to this width if larger.
        - ``every_nth_frame``: skip frames between captures (1 = every frame).
        """
        if self._frame_dir is not None:
            raise ZendriverMCPError("A screencast is already running; stop it first.")
        if fmt not in {"jpeg", "png"}:
            raise ZendriverMCPError(f"fmt must be 'jpeg' or 'png', got {fmt!r}")

        target = (
            Path(output_dir).expanduser().resolve()
            if output_dir
            else Path(tempfile.mkdtemp(prefix="zendriver-screencast-"))
        )
        target.mkdir(parents=True, exist_ok=True)

        tab = self.session.page
        extension = "jpg" if fmt == "jpeg" else "png"

        async def on_frame(event: cdp.page.ScreencastFrame) -> None:
            assert self._frame_dir is not None
            index = self._frame_count
            self._frame_count += 1
            path = self._frame_dir / f"frame-{index:06d}.{extension}"
            path.write_bytes(base64.b64decode(event.data))
            # Acking tells Chrome we consumed the frame - without it the stream stalls.
            await tab.send(cdp.page.screencast_frame_ack(session_id=event.session_id))

        self._frame_dir = target
        self._frame_count = 0
        self._frame_format = extension
        self._handler = on_frame

        tab.add_handler(cdp.page.ScreencastFrame, on_frame)
        await tab.send(
            cdp.page.start_screencast(
                format_=fmt,
                quality=quality,
                max_width=max_width,
                every_nth_frame=every_nth_frame,
            )
        )
        return ToolResponse(
            summary=f"Screencast started -> {target}",
            data={"format": fmt, "quality": quality, "every_nth_frame": every_nth_frame},
            files=[str(target)],
        ).to_dict()

    async def stop_screencast(self) -> dict[str, object]:
        """Stop the active screencast and return the frame directory + count."""
        if self._frame_dir is None or self._handler is None:
            raise ZendriverMCPError("No screencast in progress.")

        tab = self.session.page
        await tab.send(cdp.page.stop_screencast())

        # Drain in-flight frame events before detaching the handler.
        await asyncio.sleep(0.2)
        tab.handlers.get(cdp.page.ScreencastFrame, []).remove(self._handler)

        directory = self._frame_dir
        frames = self._frame_count
        self._frame_dir = None
        self._frame_count = 0
        self._handler = None

        return ToolResponse(
            summary=f"Screencast stopped: {frames} frames in {directory}",
            data={"frame_count": frames, "format": self._frame_format},
            files=[str(directory)],
        ).to_dict()
