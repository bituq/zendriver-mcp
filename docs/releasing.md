# Releasing

## One-time setup (PyPI Trusted Publishing)

1. Go to https://pypi.org/manage/account/publishing/ and add a pending
   publisher:
   - PyPI project name: `zendriver-mcp`
   - Owner: `bituq`
   - Repository name: `zendriver-mcp`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
2. On GitHub, add an `Environment` named `pypi` to the repo settings - no
   reviewers or protection rules are required, but the environment must
   exist so the workflow can target it.

With that in place, the workflow publishes without any API tokens.

## Cutting a release

1. Bump the version in `pyproject.toml` (e.g. `0.2.0` -> `0.3.0`).
2. Update `CHANGELOG.md`: rename the `[Unreleased]` heading to the new
   version with today's date; add a fresh empty `[Unreleased]`.
3. Commit: `git commit -am "Release 0.3.0"`.
4. Tag: `git tag v0.3.0`.
5. Push: `git push && git push --tags`.

The `Publish to PyPI` workflow runs on the tag push:
- Builds `sdist` and `wheel` with `uv build`
- Uploads them as a job artefact
- Publishes via Trusted Publishing (OIDC, no tokens needed)

## Manual publish (fallback)

If for some reason you want to publish by hand:

```sh
uv build
uv run python -m twine upload dist/*  # use a PyPI API token
```

## Versioning

Semver. Breaking changes bump major. New features bump minor. Bug fixes
bump patch.
