"""Inspect AX node relationships."""

from __future__ import annotations

import asyncio

import zendriver as zd

from src.tools.accessibility import _raw_get_full_ax_tree


async def main() -> None:
    browser = await zd.start(headless=True)
    try:
        tab = await browser.get("https://example.com")
        await asyncio.sleep(0.5)

        raw = await tab.send(_raw_get_full_ax_tree())
        print(f"Total: {len(raw)}")
        for n in raw:
            nid = n.get("nodeId")
            role = (n.get("role") or {}).get("value")
            name = (n.get("name") or {}).get("value")
            parent = n.get("parentId")
            kids = n.get("childIds") or []
            ignored = n.get("ignored")
            print(
                f"  id={nid} role={role!r} name={name!r:40.40} parent={parent} "
                f"childIds={kids} ignored={ignored}"
            )
    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(main())
