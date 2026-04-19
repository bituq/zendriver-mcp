"""Round-trip tests for cookie serialisation (no browser needed)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from zendriver import cdp


@pytest.fixture
def sample_cookie_json() -> list[dict[str, object]]:
    return [
        {
            "name": "sid",
            "value": "abc123",
            "domain": ".example.com",
            "path": "/",
            "secure": True,
            "httpOnly": True,
        },
        {
            "name": "pref",
            "value": "dark",
            "domain": "example.com",
            "path": "/",
            "secure": False,
            "httpOnly": False,
        },
    ]


def test_cookie_param_roundtrip(sample_cookie_json: list[dict[str, object]]) -> None:
    for raw in sample_cookie_json:
        cp = cdp.network.CookieParam.from_json(raw)
        back = cp.to_json()
        assert back["name"] == raw["name"]
        assert back["value"] == raw["value"]
        assert back["domain"] == raw["domain"]


def test_cookie_param_rejects_missing_required_fields() -> None:
    with pytest.raises((KeyError, TypeError)):
        cdp.network.CookieParam.from_json({"value": "only"})


def test_export_file_contains_sorted_keys(
    tmp_path: Path, sample_cookie_json: list[dict[str, object]]
) -> None:
    # Mimic what CookieTools.export_cookies does: serialise with sort_keys.
    out = tmp_path / "cookies.json"
    params = [cdp.network.CookieParam.from_json(c) for c in sample_cookie_json]
    out.write_text(json.dumps([p.to_json() for p in params], indent=2, sort_keys=True))
    loaded = json.loads(out.read_text())
    assert len(loaded) == 2
    # sort_keys means "domain" precedes "name" etc.
    first_keys = list(loaded[0].keys())
    assert first_keys == sorted(first_keys)
