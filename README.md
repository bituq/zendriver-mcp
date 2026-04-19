# zendriver-mcp

An MCP (Model Context Protocol) server that gives LLM agents a fully-featured,
**undetectable** browser, backed by
[Zendriver](https://github.com/cdpdriver/zendriver) and the raw Chrome DevTools
Protocol. Think of it as `chrome-devtools-mcp`'s sibling, trained to go where
Puppeteer gets blocked.

> **Fork notice.** This project is a fork of
> [ShubhamChoulkar/Zendriver-MCP](https://github.com/ShubhamChoulkar/Zendriver-MCP).
> The token-optimised DOM walker ("interaction tree") and the original 45+ MCP
> tools are Shubham's work, used under the MIT licence. We keep that baseline
> intact and extend it with stealth, DevTools parity, and quality-of-life
> features. See [CHANGELOG.md](./CHANGELOG.md) for the running list.

## Why this fork exists

Google's `chrome-devtools-mcp` is brilliant for performance work (Lighthouse,
traces, heap snapshots), but it speaks Puppeteer - which means
`navigator.webdriver` and Cloudflare walls. Zendriver speaks raw CDP and keeps
a realistic fingerprint, so agents can actually use the real web.

We pair that with the DevTools-style tooling agents expect:

| Capability | chrome-devtools-mcp | zendriver-mcp |
|---|---|---|
| Undetected browsing (Cloudflare, Akamai, PX) | no | yes |
| Performance traces | yes | planned |
| Lighthouse audits | yes | planned (via subprocess) |
| Heap snapshots | yes | planned |
| Token-optimised DOM walker | snapshot + uids | interaction tree + uids |
| Human-like input (mouse paths, typing delays) | no | planned |

## Roadmap

**Phase 1 - stealth (in progress)**
- `bypass_cloudflare` tool wrapping zendriver's challenge solver
- Human-like input: bezier mouse paths, per-keystroke typing delays
- `set_user_agent`, `set_locale`, `set_timezone`

**Phase 2 - DevTools parity**
- Emulation: viewport, device, CPU / network throttling
- Performance traces (`Tracing.start` / `Tracing.end`)
- Heap snapshots (`HeapProfiler.takeHeapSnapshot`)
- Lighthouse wrapper via subprocess against the remote debugging port

**Phase 3 - quality of life**
- Screencast / video
- CDP a11y-tree uids as a stable sibling to the interaction tree
- Structured `McpResponse` formatter instead of string blobs
- Wider test coverage, richer error taxonomy, docs site

## Install

Requires Python 3.10+ (we pin 3.12) and [`uv`](https://docs.astral.sh/uv/).

```sh
git clone https://github.com/bituq/zendriver-mcp.git
cd zendriver-mcp
uv sync
```

## Use with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "zendriver": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/zendriver-mcp", "run", "python", "run.py"]
    }
  }
}
```

## Token-optimised DOM walker

The star feature from upstream: instead of dumping HTML or a verbose element
tree to the model, the walker emits compact rows like
`{"id": 1, "t": "btn", "l": "Search", "r": "hdr"}`.

- **Compact keys**: `t` (type), `l` (label), `r` (region)
- **Smart labels**: inferred from `aria-label`, `aria-labelledby`, associated
  `<label>`, `placeholder`, text, `title`, `alt`
- **Noise filtering**: SVG internals, nested interactive children skipped
- **Region tagging**: `hdr`, `nav`, `main`, `side`, `ftr`, `dlg`
- **Type compression**: `button` -> `btn`, `checkbox` -> `chk`, etc.

Reported reduction on perplexity.ai: ~96% fewer tokens than raw HTML (~11k ->
~400). Usage:

```python
tree = get_interaction_tree()           # [{"id": 1, "t": "btn", "l": "Submit", "r": "main"}, ...]
click("1")                              # clicks id=1
type_text("hello", "3")                 # types into id=3
```

## Development

```sh
uv sync
uv run ruff check .
uv run mypy src
uv run pytest
```

CI runs the same three on every push / PR.

## License

MIT. See [LICENSE](./LICENSE). Upstream components remain under their original
MIT license.
