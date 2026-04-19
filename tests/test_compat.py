"""Regression tests for the zendriver Transaction patch.

The patch converts parser errors inside ``Transaction.__call__`` into
future exceptions instead of letting them escape into the Listener task
(where they get swallowed silently).
"""

from __future__ import annotations

import pytest
from zendriver.core.connection import ProtocolException, Transaction

from src import compat  # noqa: F401  # triggers the patch


def test_patch_marker_present() -> None:
    assert getattr(Transaction, compat._PATCH_ATTR, False) is True


def _cdp_generator(raise_on_send):  # type: ignore[no-untyped-def]
    """Minimal CDP generator that raises the given error when fed a response."""
    response = yield {"method": "Test.command", "params": {}}
    if raise_on_send:
        raise raise_on_send
    return response


async def test_parser_value_error_becomes_future_exception() -> None:
    gen = _cdp_generator(ValueError("'uninteresting' is not a valid AXPropertyName"))
    tx = Transaction(gen)  # picks up the running loop from asyncio

    # Simulate the Listener handing back a response.
    tx(**{"id": 1, "result": {"nodes": [{"role": {"value": "x"}}]}})

    with pytest.raises(ValueError, match="uninteresting"):
        await tx


async def test_happy_path_still_completes_with_result() -> None:
    gen = _cdp_generator(None)
    tx = Transaction(gen)

    tx(**{"id": 2, "result": {"ok": True}})
    assert await tx == {"ok": True}


async def test_cdp_error_response_sets_protocol_exception() -> None:
    gen = _cdp_generator(None)
    tx = Transaction(gen)

    tx(**{"id": 3, "error": {"code": -32000, "message": "oops"}})
    with pytest.raises(ProtocolException):
        await tx
