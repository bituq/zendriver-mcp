# Getting started

## Install

Prereqs: Python 3.10+ and a Chrome / Chromium install. Pick one:

```sh
# Zero-setup, resolves the latest release every run
uvx zendriver-mcp

# Install once, invoke many
uv tool install zendriver-mcp
pipx install zendriver-mcp
pip install zendriver-mcp

# Working on the server itself? Clone + sync
git clone https://github.com/bituq/zendriver-mcp.git
cd zendriver-mcp
uv sync
```

## Hooking it up to an MCP client

### Claude Desktop / Claude Code

Edit `claude_desktop_config.json` (Desktop) or `~/.claude.json`
(Code, under the `mcpServers` key):

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

Restart the client. You should see ~96 `zendriver__*` tools in the tool
list. Swap ``"command": "uvx"`` for ``"command": "zendriver-mcp"`` if you
prefer a permanent install via ``uv tool install zendriver-mcp``.

### Other MCP clients

Any client that speaks stdio MCP will work. Point it at
`uv run zendriver-mcp` from this directory.

## First steps

1. Ask the agent to `start_browser()`. A real Chrome window will open.
2. Use `navigate(url)` to go somewhere.
3. Use `get_interaction_tree()` to see an LLM-friendly view of the page.
4. `click("1")` (or whichever numeric id) to interact.

For deterministic long flows, prefer `get_accessibility_snapshot()` +
`click_by_uid(uid)` - uids remain valid across re-renders.

## Optional: Lighthouse

If you want `run_lighthouse` to work, install the CLI separately (it's a
Node package, not a Python dep):

```sh
npm install -g lighthouse
```

Then `run_lighthouse(url)` will run against the same browser Zendriver is
driving, no second launch.

## CLI flags

`zendriver-mcp` takes:

- `--browser-path /path/to/chrome` - point at a specific Chrome binary, handy
  for Chrome-for-Testing or Canary builds
- `--transport stdio` - only stdio is supported right now

## Troubleshooting

- **Chrome won't launch in a container or on a headless server.** Zendriver
  needs a real Chrome process. On Linux without a display, run under Xvfb or
  use `zendriver-docker`.
- **The browser opens but every site says "Access denied".** The fingerprint
  is intact, but your IP is probably flagged. Use a residential proxy via
  the upstream browser args (support for a first-class `set_proxy` tool is
  on the roadmap).
- **Tools say "Browser not started".** Call `start_browser()` first. It's a
  one-shot per session.
