"""Quick live smoke test: start a browser, navigate, snapshot, stop.

Run with ``uv run python scripts/integration_smoke.py``. Requires Chrome.
Intended as a sanity check, not part of the automated pytest suite.
"""

from __future__ import annotations

import asyncio
import sys


async def main() -> int:
    # Import here so the module file is valid Python even without deps.
    from src.session import BrowserSession

    session = BrowserSession.get_instance()
    await session.start(headless=True)
    try:
        await session.navigate("https://example.com")
        await asyncio.sleep(1.0)

        from src.tools import (
            get_accessibility_snapshot,
            get_interaction_tree,
            start_screencast,
            stop_screencast,
        )

        tree = await get_interaction_tree()
        print(f"interaction_tree len: {len(tree) if hasattr(tree, '__len__') else 'n/a'}")

        ax = await get_accessibility_snapshot(max_nodes=40)
        print(f"ax summary: {ax['summary']}, uids: {ax['data'].get('uid_count')}")

        cast = await start_screencast(fmt="jpeg", quality=60, max_width=800)
        print(f"screencast: {cast['summary']}")
        await asyncio.sleep(0.8)
        result = await stop_screencast()
        print(f"screencast stopped: {result['summary']}")

        return 0
    finally:
        await session.stop()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
