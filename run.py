"""Thin compatibility shim. Prefer `uv run zendriver-mcp` or `python -m src.server`."""

from __future__ import annotations

from src.server import main

if __name__ == "__main__":
    main()
