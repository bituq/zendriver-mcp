# Changelog

All notable changes to this project will be documented here.
Format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-04-19

### Added - round 2 audit follow-up
- **Path sandbox** (`src/artifacts.py`): every file-writing tool now
  rejects paths outside ``$HOME`` / the system temp dir /
  ``$ZENDRIVER_MCP_ARTIFACT_ROOT``. No more `/etc/passwd` overwrites.
  Applies to `export_cookies`, `stop_trace`, `take_heap_snapshot`,
  `screenshot`, `start_screencast`, `export_screencast_mp4`,
  `run_lighthouse`.
- `export_cookies` writes with ``chmod 0o600`` so session tokens aren't
  world-readable.
- `mock_response` rejects request bodies larger than 10 MiB.
- `ToolBase.resolve_selector` + `ZENDRIVER_ID_ATTR` constant dedupe the
  numeric-id-to-CSS-selector pattern across elements / humanlike.
- `ToolBase.__init__` auto-registers `_reset_state` callbacks, so new
  stateful tools can't forget the session-cleanup hook.
- `tests/conftest.py` with an autouse `reset_browser_session` fixture +
  `fresh_session` / `stub_mcp` fixtures.

### Fixed - round 2
- `press_key(" ")` (and `Space`) now actually inserts a space. The
  metadata branch skipped `text=`, so the key event fired but no
  character ever landed in the input.
- `type_text(replace=True)` no longer double-clicks the target; the
  redundant post-clear click was toggling date-pickers / checkboxes off.
- `fill_form` catches `json.JSONDecodeError` and raises the typed
  `ZendriverMCPError` instead of leaking an untyped traceback.
- `press_key` uses the correct CDP ``code`` for digits and punctuation
  (`Digit1`, `Minus`, `Semicolon`, ...).
- Interception race: `on_paused` captures the tab reference *inside*
  `self._lock` and exits cleanly if `stop_browser` ran mid-handler;
  previously a paused request could stay stuck in Chrome indefinitely.
- Screencast straggler-frame: `stop_screencast` clears `_frame_dir`
  before the drain sleep, so a late `screencastFrame` event no longer
  raises `AssertionError` from the Listener task.
- `compat._safe_transaction_call` guards against `EventTransaction`
  instances whose `__cdp_obj__` is None.
- `get_accessibility_snapshot` now renders every top-level AX root
  instead of silently dropping all but the first (iframes / OOPIF
  embedded content).
- `get_page_info` reads `document.title` via `page.evaluate` so the
  response is always a real string, never a bound-method repr.
- `clear_user_agent` queries `Browser.getVersion` and restores the
  real UA; empty string was leaving a *more* fingerprintable client.
- Dropped stray `--chrome-flags=--headless=false` from the Lighthouse
  invocation.

### Regression tests added
- `test_artifacts_sandbox.py` - path sandbox allow/deny paths.
- `test_forms_press_key.py` - VK metadata carries `text`, single-char
  code mapping.
- `test_escape_js.py` - table-driven JS-escape coverage.
- `test_accessibility_uid_stability.py` - uid reuse across snapshots.

Tool count still 96. Test count: 42 → 75.

## [0.2.0] - 2026-04-19

### Fixed

**Tool timeouts prevent session-killing hangs**
- Every MCP tool now runs inside `asyncio.wait_for` with a configurable
  budget (default 60s, or the `ZENDRIVER_MCP_TOOL_TIMEOUT` env var).
  Slow tools get higher ceilings: `run_lighthouse` 300s,
  `export_screencast_mp4` 300s, `take_heap_snapshot` 180s, `bypass_cloudflare`
  120s, `get_accessibility_snapshot` 30s, etc. Before this a single hung
  CDP command could freeze the stdio loop until the client disconnected,
  tearing down the whole session. New `ToolTimeoutError` surfaces the
  boundary with the tool name and budget.

**Parser hangs on enum-version skew (root cause patch)**
- Zendriver's CDP bindings hard-code enum members from the Chrome revision
  they were generated against. When Chrome ships a new value (today's
  offender: `AXPropertyName.uninteresting`) the generated `from_json`
  raises `ValueError`, which propagates into `Transaction.__call__`,
  which is driven by the Listener task, which silently swallows the error
  and leaves the caller's future unresolved. Affected tools hang until
  our timeout guard fires.
- `src/compat.py` monkey-patches `Transaction.__call__` to convert *any*
  parser exception into a future exception. Fail-fast with the real
  error instead of a timeout. Imported with side effects inside
  `src/session.py` so the patch is in place before the first CDP
  round-trip. One patch immunises every tool against this class of bug.

**`get_accessibility_snapshot` returned only the root node**
- Two bugs in one flow. First the above parser hang. Then even with the
  hang removed the render pass emitted only `RootWebArea` because real
  Chrome puts an `ignored=true, role="none"` wrapper between the root
  and the content, and the filter treated "ignored && not interactive"
  as a hard prune.
- Rewrote the render pass to treat skipped nodes as transparent: they
  return their rendered children to the parent instead of becoming
  dead-ends. Noise roles (`none`, `generic`, `presentation`,
  `InlineTextBox`, `StaticText`) are recognised explicitly.
  Interactive-role set expanded (`menuitemcheckbox`, `menuitemradio`,
  `treeitem`). Root detected via `parentId is None`, not `raw_nodes[0]`.
- AX snapshot for example.com now returns 5 nodes (RootWebArea,
  heading, 2 paragraphs, link) in ~10 ms; previously it hung 30 s and
  timed out.
- `src/tools/accessibility.py` also bypasses zendriver's AX parser
  entirely via a local `_raw_get_full_ax_tree` generator that returns
  the CDP response dict verbatim. Safer than relying on the compat
  patch alone.

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

Tool count: 88 -> 96. Test count: 24 -> 38.

### Added - initial fork shape

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
