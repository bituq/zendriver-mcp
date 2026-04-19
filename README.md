# zendriver-mcp

**Undetectable browser automation for LLM agents, spoken over MCP.**

`zendriver-mcp` is an [MCP](https://modelcontextprotocol.io) server that gives
your coding agent (Claude, Cursor, Gemini, Copilot) a real Chrome browser it
can actually use on the real web - behind Cloudflare, behind login walls, on
pages that detect and block WebDriver.

It's built on [Zendriver](https://github.com/cdpdriver/zendriver), which speaks
the Chrome DevTools Protocol directly instead of going through WebDriver. That
means no `navigator.webdriver` flag, no headless telltales, and a fingerprint
that looks like an ordinary Chrome install.

On top of that foundation, `zendriver-mcp` layers everything an agent needs
to get work done: a token-efficient DOM walker, an accessibility tree with
stable uids, performance traces, Lighthouse audits, heap snapshots, human-like
input, device emulation, cookie round-tripping, and more - **88 tools across
19 modules**.

## Highlights

- **Undetectable by design.** Zendriver keeps a clean fingerprint; we ship a
  Cloudflare Turnstile solver, identity overrides (UA, locale, timezone,
  geolocation), and bezier-curve mouse movement plus gaussian typing timing.
- **Token-efficient DOM.** Two ways to see the page - the upstream DOM walker
  that reports 96% fewer tokens than raw HTML, and a CDP accessibility tree
  keyed by stable uids that survive re-renders.
- **Full DevTools parity.** Performance traces that load in Chrome DevTools,
  heap snapshots in the standard `.heapsnapshot` format, Lighthouse audits
  via the Lighthouse CLI reusing the same browser.
- **Session round-tripping.** Export all cookies (including HTTP-only ones)
  to JSON, re-import on the next session. Log in once, reuse everywhere.
- **Emulation.** iPhone 15 Pro, Pixel 8, iPad Pro, and desktop presets; CPU
  throttling; Slow 3G / Fast 3G / 4G / offline network profiles; force
  `prefers-color-scheme`.
- **Screencasts.** Write frames to disk as JPEG or PNG at configurable FPS.

## Tool catalogue

| Module | Tools |
|---|---|
| `browser` | start, stop, status |
| `navigation` | navigate, back, forward, reload, page info |
| `tabs` | new / list / switch / close |
| `elements` | click, type, clear, focus, select, upload |
| `query` | find element(s), text, attributes, buttons, inputs |
| `content` | HTML, text, interaction tree, scroll |
| `storage` | cookies (document.cookie), localStorage |
| `logging` | network + console logs, wait-for-request |
| `forms` | fill form, submit, key press, mouse click |
| `utils` | screenshot, execute JS, wait, security audit |
| `stealth` | Cloudflare bypass, UA / locale / timezone / geolocation overrides |
| `humanlike` | human_click, human_type, estimated_typing_duration |
| `emulation` | viewport, device presets, CPU + network throttle, media |
| `devtools` | start/stop trace, take heap snapshot |
| `lighthouse` | run audit, check CLI availability |
| `screencast` | start / stop (writes frame directory) |
| `accessibility` | AX snapshot with stable uids, click_by_uid, describe_uid |
| `cookies` | export / import / list / clear (CDP-level, all origins) |
| `network_control` | block URLs, extra headers, bypass service worker |
| `permissions` | grant / reset, list names |

Full signatures live in the docstrings of `src/tools/*.py` and are auto-listed
by the MCP handshake.

## Install

Requires Python 3.10+ (we pin 3.12) and [`uv`](https://docs.astral.sh/uv/).

```sh
git clone https://github.com/bituq/zendriver-mcp.git
cd zendriver-mcp
uv sync
```

## Use with Claude Desktop / Claude Code

```json
{
  "mcpServers": {
    "zendriver": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/zendriver-mcp",
        "run",
        "zendriver-mcp"
      ]
    }
  }
}
```

Optional flags on the CLI:

- `--browser-path /path/to/chrome` - point at a specific Chrome binary
- `--transport stdio` - only stdio for now; SSE/HTTP arrive when upstream
  `mcp` ships stable support

## The 30-second tour

```python
# Ask the browser to start, log in once, save the session.
await start_browser()
await navigate("https://example.com/login")
await fill_form({"#email": "me@me.com", "#pw": "..."})
await export_cookies("~/sessions/example.json")

# Next run: skip the login entirely.
await start_browser()
await import_cookies("~/sessions/example.json")
await navigate("https://example.com/dashboard")

# Get an accessibility snapshot, click by stable uid.
snap = await get_accessibility_snapshot()
await click_by_uid("ax_1b2c3d4e")

# Record a performance trace while you click around.
await start_trace()
await human_click(selector="#buy-now")
await stop_trace("/tmp/buy-flow.json")   # loads in Chrome DevTools

# Run Lighthouse against the current browser.
await run_lighthouse("https://example.com", form_factor="mobile")
```

## Token-optimised DOM walker

The interaction tree emits compact rows like
`{"id": 1, "t": "btn", "l": "Search", "r": "hdr"}`:

- **Compact keys**: `t` (type), `l` (label), `r` (region)
- **Smart labels**: inferred from `aria-label`, `aria-labelledby`, associated
  `<label>`, `placeholder`, text, `title`, `alt`
- **Noise filtering**: SVG internals, nested interactive children skipped
- **Region tagging**: `hdr`, `nav`, `main`, `side`, `ftr`, `dlg`
- **Type compression**: `button` -> `btn`, `checkbox` -> `chk`, etc.

Reported reduction on perplexity.ai: ~96% fewer tokens than raw HTML (~11k ->
~400).

For flows that span multiple actions, prefer `get_accessibility_snapshot` +
`click_by_uid` - the uids stay valid as long as the underlying backend node
survives, even across re-renders.

## Development

```sh
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```

CI runs the same four on every push and PR.

## Roadmap

- Full `McpResponse` adoption across all legacy tools (phase-3 envelope is
  opt-in for now)
- Video export (`.mp4`) via ffmpeg from the screencast frames
- Request interception and response rewriting (`Fetch.enable`)
- Proxy configuration tool
- `uv` / PyPI publication

## License

MIT. See [LICENSE](./LICENSE).

## Acknowledgements

- [Zendriver](https://github.com/cdpdriver/zendriver) does the heavy lifting
  underneath.
- The token-optimised DOM walker and the original 49-tool foundation come from
  [ShubhamChoulkar/Zendriver-MCP](https://github.com/ShubhamChoulkar/Zendriver-MCP).
  This project started as a fork and has since grown its own identity and
  feature set.
