# Changelog

All notable changes to this project will be documented here.
Format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

**Video export**
- `export_screencast_mp4(frames_dir, output_path, fps)`: stitch screencast
  frames into an mp4 via ffmpeg. Uses libx264 + yuv420p + `+faststart`
  so the output plays in browsers and QuickTime without re-encoding.
- `check_ffmpeg_available()` surfaces whether the CLI is installed.

**Request interception / mocking**
- New `InterceptionTools` module backed by `Fetch.enable` + a persistent
  `requestPaused` handler.
- `mock_response(url_pattern, status, body, headers)` returns a rule id;
  every matching request gets the mocked response.
- `fail_requests(url_pattern, error_reason)` drops matching requests with
  a CDP `Network.ErrorReason` value (e.g. `BlockedByClient`,
  `InternetDisconnected`, `TimedOut`).
- `list_interceptions()` and `stop_interception(rule_id?)` manage rules.
- Each rule tracks a `match_count` so tests can assert "this mock fired".

**Proxy**
- `configure_proxy(proxy_url, user_data_dir, headless)` and
  `clear_proxy(...)`. Chrome can't swap proxies at runtime so we restart
  the browser; pass a `user_data_dir` to preserve the logged-in session.

**PyPI release workflow**
- `.github/workflows/publish.yml`: on `v*` tag push, builds sdist + wheel
  with `uv build` and publishes via Trusted Publishing (OIDC, no API
  tokens needed on the repo side).
- `docs/releasing.md` walks through PyPI pending-publisher setup, cutting
  a release, and the manual fallback.

**ToolResponse adoption**
- `BrowserTools.get_browser_status`, `NavigationTools.get_page_info`, and
  `TabTools.list_tabs` now return the `ToolResponse` envelope
  (`{"summary", "data"}`) so agents can programmatically inspect state
  instead of parsing strings.

**Docs**
- `docs/recipes/mock-api-responses.md` covers `mock_response`,
  `fail_requests`, and rule management.
- `docs/tool-reference.md` updated to cover proxy, interception, and the
  new screencast tools.

Tool count: 88 -> 96.

## [0.2.0] - 2026-04-19

### Added

**Housekeeping**
- `uv` project layout, pinned to Python 3.12.
- Ruff + mypy config, pytest scaffold with smoke tests.
- GitHub Actions CI (ruff, ruff format --check, mypy, pytest).
- `LICENSE` file (MIT) and PyPI-ready package metadata (keywords,
  classifiers, project URLs).
- `docs/` directory with getting-started, full tool reference, and three
  recipe guides (login-reuse, Cloudflare, performance audit).
- Manual integration smoke: `scripts/integration_smoke.py`.

**Stealth + human-like input**
- `StealthTools`: `bypass_cloudflare`, `is_cloudflare_challenge_present`,
  `set_user_agent`, `clear_user_agent`, `set_locale`, `set_timezone`,
  `set_geolocation`.
- `HumanInputTools`: `human_click`, `human_type`,
  `estimated_typing_duration`, built on bezier mouse paths and gaussian
  keystroke timing primitives in `src/humaninput.py`.

**DevTools parity**
- `EmulationTools`: viewport, device profiles (iPhone 15 Pro, Pixel 8,
  iPad Pro, Desktop 1080p), CPU throttle, network presets (offline /
  slow-3g / fast-3g / 4g / no-throttling), `emulate_media`.
- `DevToolsTools`: `start_trace` / `stop_trace` producing DevTools-loadable
  JSON; `take_heap_snapshot` producing `.heapsnapshot` files.
- `LighthouseTools`: `run_lighthouse` and `check_lighthouse_available`,
  shelling out to the Lighthouse CLI against the browser's remote
  debugging port.

**Session + network control**
- `CookieTools`: `export_cookies`, `import_cookies`, `list_all_cookies`,
  `clear_all_cookies` - CDP-level, covers HTTP-only cookies and all
  origins (upstream `storage.get_cookies` only reads `document.cookie`).
- `NetworkControlTools`: `block_urls`, `unblock_all_urls`,
  `set_extra_headers`, `bypass_service_worker`.
- `PermissionsTools`: `grant_permissions`, `reset_permissions`,
  `list_permission_names` with a curated short-name table.

**Quality of life**
- `ScreencastTools`: `start_screencast` / `stop_screencast` using CDP
  `Page.startScreencast` events, writing frames to disk as JPEG or PNG.
- `AccessibilityTools`: `get_accessibility_snapshot` returns the CDP AX
  tree keyed by stable uids, `click_by_uid` performs deterministic
  interaction, `describe_uid` returns cached metadata.
- `ToolResponse` envelope (`src/response.py`) for structured dict returns
  with `summary` / `data` / `files` keys.
- Richer error taxonomy: `CloudflareChallengeError`, `TracingError`,
  `LighthouseNotInstalledError`, `AccessibilityUidError`.
- Consolidated CLI in `src/server.py` with `--browser-path` and
  `--transport` flags; `run.py` kept as a compatibility shim.

### Fixed
- `type_text` referenced an undefined `self._tab`; now sends
  `cdp.input_.insert_text` through the active tab.

### Changed
- `ToolBase._register_tools` is now an `@abstractmethod`, matching actual
  usage in subclasses.
- Bumped to `0.2.0` to signal the new shape.

Tool count: upstream 49 -> 88.

## Acknowledgements

The token-optimised DOM walker and the original 49-tool foundation come from
[ShubhamChoulkar/Zendriver-MCP](https://github.com/ShubhamChoulkar/Zendriver-MCP).
This release takes that base and grows it into a full DevTools + stealth
automation suite.
