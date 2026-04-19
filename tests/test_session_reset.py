"""Session reset callbacks fire on stop_browser and wipe tool state."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.session import BrowserSession
from src.tools.accessibility import AccessibilityTools, _UidEntry
from src.tools.devtools import DevToolsTools
from src.tools.interception import InterceptionTools, _Rule
from src.tools.screencast import ScreencastTools


@pytest.fixture
def fresh_session() -> BrowserSession:
    BrowserSession._instance = None
    return BrowserSession.get_instance()


def _stub_mcp() -> MagicMock:
    mcp = MagicMock()
    mcp.tool.return_value = lambda fn: fn
    return mcp


async def test_stop_fires_registered_callbacks(fresh_session: BrowserSession) -> None:
    calls: list[str] = []
    fresh_session.register_reset_callback(lambda: calls.append("a"))
    fresh_session.register_reset_callback(lambda: calls.append("b"))
    # stop() returns early when there's no browser, so fake the attribute.
    fresh_session._browser = MagicMock()
    fresh_session._browser.stop = _async_noop
    await fresh_session.stop()
    assert calls == ["a", "b"]


async def _async_noop() -> None:
    return None


async def test_stop_runs_callbacks_even_if_one_raises(
    fresh_session: BrowserSession,
) -> None:
    def bad() -> None:
        raise RuntimeError("boom")

    calls: list[str] = []
    fresh_session.register_reset_callback(bad)
    fresh_session.register_reset_callback(lambda: calls.append("after_bad"))
    fresh_session._browser = MagicMock()
    fresh_session._browser.stop = _async_noop
    await fresh_session.stop()
    assert calls == ["after_bad"]


async def test_duplicate_registration_is_idempotent(
    fresh_session: BrowserSession,
) -> None:
    counter = {"n": 0}

    def inc() -> None:
        counter["n"] += 1

    fresh_session.register_reset_callback(inc)
    fresh_session.register_reset_callback(inc)
    fresh_session._browser = MagicMock()
    fresh_session._browser.stop = _async_noop
    await fresh_session.stop()
    assert counter["n"] == 1


async def test_tools_reset_on_stop(fresh_session: BrowserSession) -> None:
    interception = InterceptionTools(_stub_mcp())
    interception._rules.append(_Rule(id="rule_1", url_pattern="*", action="mock"))
    interception._handler = lambda e: None  # type: ignore[assignment]
    interception._next_id = 42

    devtools = DevToolsTools(_stub_mcp())
    devtools._trace_events = [{"cat": "x"}]

    screencast = ScreencastTools(_stub_mcp())
    screencast._frame_dir = Path("/tmp/stale")
    screencast._frame_count = 99

    accessibility = AccessibilityTools(_stub_mcp())
    accessibility._uids["ax_old"] = _UidEntry(backend_node_id=1, role="button", name="")

    fresh_session._browser = MagicMock()
    fresh_session._browser.stop = _async_noop
    await fresh_session.stop()

    assert interception._rules == []
    assert interception._handler is None
    assert interception._next_id == 0
    assert devtools._trace_events is None
    assert screencast._frame_dir is None
    assert screencast._frame_count == 0
    assert accessibility._uids == {}
