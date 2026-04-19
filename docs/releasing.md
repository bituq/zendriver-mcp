# Releasing

Tagging `v*` triggers [`.github/workflows/publish.yml`](https://github.com/bituq/zendriver-mcp/blob/main/.github/workflows/publish.yml),
which publishes to two places in sequence:

1. **PyPI** via Trusted Publishing (OIDC).
2. **MCP Registry** via `mcp-publisher` + GitHub OIDC, so the server is
   discoverable as `io.github.bituq/zendriver-mcp`.

Both use GitHub's OIDC token. There are **no long-lived secrets** to
rotate.

## One-time setup

### PyPI Trusted Publishing

1. Go to https://pypi.org/manage/account/publishing/ and add a pending
   publisher:
     - PyPI project name: `zendriver-mcp`
     - Owner: `bituq`
     - Repository name: `zendriver-mcp`
     - Workflow name: `publish.yml`
     - Environment name: `pypi`
2. On GitHub, add an `Environment` named `pypi` to the repo settings
   (no reviewers or protection rules needed, the environment just has
   to exist so the workflow can target it).

### MCP Registry

The registry uses namespace-based ownership. Anyone authenticated as
`bituq` on GitHub can publish `io.github.bituq/*`. No registry-side
setup needed beyond this - the workflow calls
`mcp-publisher login github-oidc` which reads the GitHub Actions OIDC
token and exchanges it with the registry.

### Ownership marker in README

The MCP Registry verifies PyPI package ownership by scanning for

    <!-- mcp-name: io.github.bituq/zendriver-mcp -->

in the README (PyPI surfaces README as the package description). It's
already in the file; leave it there.

## Cutting a release

1. Bump the version in `pyproject.toml` (e.g. `0.3.1` -> `0.4.0`).
2. Update `CHANGELOG.md`: rename the `[Unreleased]` heading to the new
   version with today's date; add a fresh empty `[Unreleased]`.
3. Commit: `git commit -am "Release 0.4.0"`.
4. Tag: `git tag v0.4.0`.
5. Push: `git push && git push --tags`.

The publish workflow runs on the tag push:

- **build** job: `uv build` produces sdist + wheel.
- **publish** job: uploads to PyPI via
  `pypa/gh-action-pypi-publish@release/v1`.
- **mcp-registry** job: installs `mcp-publisher`, syncs
  `server.json`'s version with the tag, and publishes via
  `mcp-publisher login github-oidc && mcp-publisher publish`.

Typical wall-clock: ~30 seconds total.

Verify after:

- PyPI: <https://pypi.org/project/zendriver-mcp/> (latest version)
- Registry:
  `curl -s "https://registry.modelcontextprotocol.io/v0/servers?search=zendriver" | jq .servers[0].server.version`

## Manual publish (fallback)

If the GH Actions path is unavailable, you can publish by hand:

```sh
uv build
uv run python -m twine upload dist/*  # needs a PyPI API token

# Optional: publish to the MCP Registry too
curl -sSL "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/').tar.gz" | tar xz mcp-publisher
./mcp-publisher login github   # opens a browser flow
./mcp-publisher publish
```

## Versioning

Semver:

- **major** (`x.0.0`): breaking changes to tool signatures or behaviour.
- **minor** (`0.x.0`): new tools or additive capabilities.
- **patch** (`0.0.x`): bug fixes, docs, internal refactors.
