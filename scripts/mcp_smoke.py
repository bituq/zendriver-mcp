"""End-to-end MCP protocol smoke test.

Spawns ``zendriver-mcp`` over stdio and exercises the MCP handshake
(initialize, tools/list) without touching a real browser. Confirms the
server speaks the protocol and advertises every tool we expect.

Run with ``uv run python scripts/mcp_smoke.py``.
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any


class StdioClient:
    def __init__(self, proc: asyncio.subprocess.Process) -> None:
        self.proc = proc
        self._next_id = 0

    async def send(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._next_id += 1
        payload = {"jsonrpc": "2.0", "id": self._next_id, "method": method}
        if params is not None:
            payload["params"] = params
        assert self.proc.stdin is not None
        assert self.proc.stdout is not None

        self.proc.stdin.write((json.dumps(payload) + "\n").encode())
        await self.proc.stdin.drain()

        # Skip notifications (no "id"), read until we see our response.
        while True:
            line = await self.proc.stdout.readline()
            if not line:
                raise RuntimeError("Server closed stdout before responding")
            data = json.loads(line.decode())
            if data.get("id") == self._next_id:
                return data
            # else: notification or response to a different id; ignore.

    async def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        assert self.proc.stdin is not None
        self.proc.stdin.write((json.dumps(payload) + "\n").encode())
        await self.proc.stdin.drain()


async def main() -> int:
    proc = await asyncio.create_subprocess_exec(
        "uv",
        "run",
        "zendriver-mcp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=".",
    )
    client = StdioClient(proc)

    try:
        init = await client.send(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "zendriver-smoke", "version": "0.0.1"},
            },
        )
        server = init["result"]["serverInfo"]
        print(f"Connected: {server['name']} v{server['version']}")

        await client.notify("notifications/initialized")

        response = await client.send("tools/list", {})
        tools = response["result"]["tools"]
        print(f"Tools advertised: {len(tools)}")

        by_name = {t["name"]: t for t in tools}
        must_have = [
            "start_browser",
            "bypass_cloudflare",
            "human_click",
            "start_trace",
            "export_cookies",
            "mock_response",
            "configure_proxy",
            "export_screencast_mp4",
            "get_accessibility_snapshot",
        ]
        missing = [name for name in must_have if name not in by_name]
        if missing:
            print(f"  MISSING: {missing}")
            return 1

        sample = by_name["mock_response"]
        print(f"Sample tool schema keys: {sorted(sample.keys())}")
        print(f"mock_response description: {sample.get('description', '')[:80]}...")

        if len(tools) < 96:
            print(f"  Expected >=96 tools, got {len(tools)}")
            return 1

        print(f"\nOK: {len(tools)} tools, all critical ones present.")
        return 0
    finally:
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=3)
        except TimeoutError:
            proc.kill()
            await proc.wait()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
