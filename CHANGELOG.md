# Changelog

All notable changes to this project will be documented here.
Format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Fork baseline with `uv` project layout, pinned to Python 3.12.
- Ruff + mypy config, pytest scaffold with smoke tests.
- GitHub Actions CI (ruff, mypy, pytest).

### Fixed
- `type_text` referenced an undefined `self._tab`; now sends
  `cdp.input_.insert_text` through the active tab.

### Changed
- `ToolBase._register_tools` is now an `@abstractmethod`, matching actual usage.

## Fork origin

Forked from [ShubhamChoulkar/Zendriver-MCP](https://github.com/ShubhamChoulkar/Zendriver-MCP)
at commit [`main`] on 2026-04-19. See upstream for the original 45+ tools
and the token-optimised DOM walker.
