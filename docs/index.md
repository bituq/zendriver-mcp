# zendriver-mcp

**Undetectable browser automation for LLM agents, spoken over MCP.**

`zendriver-mcp` is an [MCP](https://modelcontextprotocol.io) server that gives
your coding agent (Claude, Cursor, Gemini, Copilot) a real Chrome browser it
can actually use on the real web - behind Cloudflare, behind login walls, on
pages that detect and block WebDriver.

It's built on [Zendriver](https://github.com/cdpdriver/zendriver), which speaks
the Chrome DevTools Protocol directly instead of going through WebDriver. No
`navigator.webdriver` flag, no headless telltales, a fingerprint that looks
like ordinary Chrome.

On that foundation, `zendriver-mcp` layers everything an agent needs to get
work done: a token-efficient DOM walker, an accessibility tree with stable
uids, performance traces, Lighthouse audits, heap snapshots, human-like input,
device emulation, cookie round-tripping, request interception, and more -
**96 tools across 22 modules**.

## Why

Most browser-automation MCP servers lean on Puppeteer or Playwright, which
means WebDriver, which means `navigator.webdriver === true` and a shopping
list of headless telltales Cloudflare / Akamai / PerimeterX know by heart.
Agents that try to work on the real web hit bot walls immediately.

`zendriver-mcp` starts from the opposite direction:

- CDP instead of WebDriver, so the fingerprint stays clean.
- Human-like input primitives (bezier mouse paths, gaussian typing) for
  sites that look at *how* you click, not just whether you do.
- Cookie round-tripping so you log in once and reuse the session.
- A Cloudflare Turnstile solver for the last-mile interactive challenge.

## Quick start

[:material-rocket-launch: Getting started](getting-started.md){ .md-button .md-button--primary }
[:material-book-open: Tool reference](tool-reference.md){ .md-button }

Published on [PyPI](https://pypi.org/project/zendriver-mcp/) and the
[MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=zendriver)
as `io.github.bituq/zendriver-mcp`.

```sh
uvx zendriver-mcp            # zero-setup, re-resolves every run
uv tool install zendriver-mcp  # install once, invoke many
pipx install zendriver-mcp
pip install zendriver-mcp
```

Hook it up to Claude Desktop / Code in one JSON block:

```json
{
  "mcpServers": {
    "zendriver": {
      "command": "uvx",
      "args": ["zendriver-mcp"]
    }
  }
}
```

## Highlights

=== "Stealth"

    - `bypass_cloudflare` solves Turnstile challenges
    - `set_user_agent`, `set_locale`, `set_timezone`, `set_geolocation`
    - `human_click` uses bezier mouse paths
    - `human_type` uses gaussian inter-keystroke timing

=== "DevTools"

    - `start_trace` / `stop_trace` produce DevTools-loadable JSON
    - `take_heap_snapshot` produces standard `.heapsnapshot`
    - `run_lighthouse` reuses the already-running browser
    - `set_cpu_throttle`, `set_network_conditions`, `set_viewport`

=== "Session"

    - `export_cookies` / `import_cookies` work on HTTP-only cookies
    - `block_urls`, `set_extra_headers`, `bypass_service_worker`
    - `grant_permissions`, `reset_permissions`
    - `configure_proxy` restarts with a `--proxy-server` arg

=== "Observability"

    - `get_interaction_tree` - 96% fewer tokens than raw HTML
    - `get_accessibility_snapshot` - stable uids that survive re-renders
    - `start_screencast` -> `export_screencast_mp4` via ffmpeg
    - `mock_response` / `fail_requests` via `Fetch.enable`

## Recipes

Step-by-step walkthroughs for common workflows:

- [Scrape behind a login, once](recipes/scrape-behind-login.md)
- [Beat Cloudflare Turnstile](recipes/beat-cloudflare.md)
- [Performance audit an authenticated flow](recipes/performance-audit.md)
- [Mock an API response to test the UI](recipes/mock-api-responses.md)

## License

MIT. The original 49-tool foundation and the token-optimised DOM walker come
from [ShubhamChoulkar/Zendriver-MCP](https://github.com/ShubhamChoulkar/Zendriver-MCP).
