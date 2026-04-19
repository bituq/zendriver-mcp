# Changelog

All notable changes to this project will be documented here.
Format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

**Housekeeping**
- Fork baseline with `uv` project layout, pinned to Python 3.12.
- Ruff + mypy config, pytest scaffold with smoke tests.
- GitHub Actions CI (ruff, ruff format --check, mypy, pytest).

**Phase 1 - stealth + human-like input**
- `StealthTools` module:
  - `bypass_cloudflare`, `is_cloudflare_challenge_present`
  - `set_user_agent`, `clear_user_agent`, `set_locale`, `set_timezone`,
    `set_geolocation`
- Human input primitives (`src/humaninput.py`): cubic Bezier mouse paths,
  gaussian keystroke timing.
- `HumanInputTools` module: `human_click`, `human_type`,
  `estimated_typing_duration`.

**Phase 2 - DevTools parity**
- `EmulationTools` module: viewport, device profiles (iPhone 15 Pro,
  Pixel 8, iPad Pro, Desktop 1080p), CPU throttle, network conditions
  (offline / slow-3g / fast-3g / 4g / no-throttling), media emulation.
- `DevToolsTools` module: `start_trace` / `stop_trace` producing DevTools-
  loadable JSON; `take_heap_snapshot` producing `.heapsnapshot` files.
- `LighthouseTools` module: `run_lighthouse` and
  `check_lighthouse_available`, shelling out to the Lighthouse CLI against
  the browser's remote debugging port.

**Phase 3 - quality of life**
- `ScreencastTools` module: `start_screencast` / `stop_screencast` using
  CDP `Page.startScreencast` events, writing frames to disk.
- `AccessibilityTools` module: `get_accessibility_snapshot` returns the
  CDP AX tree keyed by stable uids, `click_by_uid` performs deterministic
  interaction, `describe_uid` returns cached metadata.
- `ToolResponse` envelope (`src/response.py`) for structured dict returns
  with `summary` / `data` / `files` keys.
- Richer error taxonomy: `CloudflareChallengeError`, `TracingError`,
  `LighthouseNotInstalledError`, `AccessibilityUidError`.

### Fixed
- `type_text` referenced an undefined `self._tab`; now sends
  `cdp.input_.insert_text` through the active tab.

### Changed
- `ToolBase._register_tools` is now an `@abstractmethod`, matching actual
  usage in subclasses.

Tool count: upstream 49 -> 77 after phases 1-3.

## Fork origin

Forked from [ShubhamChoulkar/Zendriver-MCP](https://github.com/ShubhamChoulkar/Zendriver-MCP)
at commit [`main`] on 2026-04-19. See upstream for the original 49 tools
and the token-optimised DOM walker.
