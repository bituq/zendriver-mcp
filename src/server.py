"""CLI entry point for the zendriver-mcp MCP server."""

from __future__ import annotations

import argparse

from src.session import BrowserSession
from src.tools import mcp


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="zendriver-mcp",
        description="Undetectable browser automation for LLM agents, spoken over MCP.",
    )
    parser.add_argument(
        "--browser-path",
        help="Absolute path to a Chrome/Chromium executable. Defaults to the system Chrome.",
    )
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio"],
        help="MCP transport. Only stdio is supported right now.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    if args.browser_path:
        BrowserSession.default_browser_path = args.browser_path
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
