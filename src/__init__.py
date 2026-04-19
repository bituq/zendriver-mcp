"""zendriver-mcp package.

Importing any ``src`` module triggers the zendriver compatibility patches
(via ``src.compat``) before a CDP round-trip can happen. This guards tests
and stand-alone scripts that import a tool module directly without going
through ``src.session``.
"""

from __future__ import annotations

from src import compat  # noqa: F401  # side-effect: patches Transaction
