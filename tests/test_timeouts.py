"""Verify every MCP tool is registered through the timeout guard."""

from __future__ import annotations

import asyncio
import inspect

import pytest

from src.errors import ToolTimeoutError
from src.tools import mcp
from src.tools.base import DEFAULT_TOOL_TIMEOUT, ToolBase


def test_default_timeout_is_positive() -> None:
    assert DEFAULT_TOOL_TIMEOUT >= 1.0


def test_every_registered_tool_is_wrapped() -> None:
    # Every MCP tool we register should carry the __zendriver_timeout__
    # marker set by ToolBase._register. Tools that skip the helper lose the
    # timeout guarantee and would reappear here.
    tools = mcp._tool_manager._tools
    non_guarded: list[str] = []
    for name, tool in tools.items():
        if not hasattr(tool.fn, "__zendriver_timeout__"):
            non_guarded.append(name)
    assert not non_guarded, f"tools bypassed the timeout wrapper: {non_guarded[:10]}"


def test_tool_timeouts_are_reasonable() -> None:
    # Guard against "zero" or nonsense timeouts slipping in; also catches
    # tools registered without the helper (marker missing -> AttributeError
    # surfaced in the earlier test, not here).
    tools = mcp._tool_manager._tools
    for name, tool in tools.items():
        budget = getattr(tool.fn, "__zendriver_timeout__", None)
        assert budget is not None and budget >= 1.0, f"{name}: {budget}"


class _StubMCP:
    """Minimal stand-in for FastMCP that records registered tools."""

    def __init__(self) -> None:
        self.registered: list = []

    def tool(self):
        def decorator(fn):
            self.registered.append(fn)
            return fn

        return decorator


class _SlowTool(ToolBase):
    def _register_tools(self) -> None:
        self._register(self.slow, timeout=0.1)

    async def slow(self) -> str:
        await asyncio.sleep(5)
        return "nope"


async def test_timeout_wrapper_raises_tool_timeout_error() -> None:
    stub = _StubMCP()
    tools = _SlowTool(stub)  # type: ignore[arg-type]
    # _register called tool(); our stub captured the wrapped callable.
    assert tools  # keep a reference so it isn't GC'd mid-test
    guarded = stub.registered[0]
    with pytest.raises(ToolTimeoutError) as excinfo:
        await guarded()
    assert excinfo.value.tool == "slow"
    assert excinfo.value.seconds == pytest.approx(0.1)


def test_timeout_wrapper_preserves_signature() -> None:
    stub = _StubMCP()
    _SlowTool(stub)  # type: ignore[arg-type]
    guarded = stub.registered[0]
    sig = inspect.signature(guarded)
    # Original coroutine has no parameters besides self; after _register the
    # `self` is bound so the tool schema sees zero params.
    assert list(sig.parameters) == []
