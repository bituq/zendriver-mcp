"""Verify our raw AX tree call works where zendriver's parsed one does not."""

from __future__ import annotations

import asyncio
import time

import zendriver as zd

from src.tools.accessibility import _raw_get_full_ax_tree


async def main() -> None:
    browser = await zd.start(headless=True)
    try:
        tab = await browser.get("https://example.com")
        await asyncio.sleep(0.5)

        print("Raw Accessibility.getFullAXTree...")
        t0 = time.perf_counter()
        raw = await asyncio.wait_for(tab.send(_raw_get_full_ax_tree()), timeout=10)
        elapsed = time.perf_counter() - t0
        print(f"  {len(raw)} raw nodes in {elapsed:.2f}s")

        roles = {n.get("role", {}).get("value") for n in raw if n.get("role")}
        print(f"  unique roles: {sorted(r for r in roles if r)}")
    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(main())
