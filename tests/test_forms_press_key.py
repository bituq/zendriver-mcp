"""Regression tests for the press_key VK table and single-char code mapping."""

from __future__ import annotations

import pytest

from src.tools.forms import _KEY_METADATA, _NON_ALPHA_CODE, _char_to_code


def test_space_metadata_carries_text() -> None:
    # Round-1 regression: Space was ``(32, "Space")`` so it hit rawKeyDown
    # without text, silently not typing a space. Ensure the third tuple
    # element is " " so press_key(" ") actually inserts a space.
    vk, code, text = _KEY_METADATA[" "]
    assert vk == 32
    assert code == "Space"
    assert text == " "


def test_enter_metadata_carries_carriage_return() -> None:
    vk, code, text = _KEY_METADATA["Enter"]
    assert vk == 13
    assert code == "Enter"
    assert text == "\r"


def test_non_text_keys_have_none_text() -> None:
    for key in ("Escape", "ArrowUp", "Home"):
        _, _, text = _KEY_METADATA[key]
        assert text is None


def test_char_to_code_handles_letters_and_digits() -> None:
    assert _char_to_code("a") == "KeyA"
    assert _char_to_code("Z") == "KeyZ"
    assert _char_to_code("1") == "Digit1"
    assert _char_to_code("9") == "Digit9"


@pytest.mark.parametrize(
    "ch,expected",
    list(_NON_ALPHA_CODE.items()),
)
def test_char_to_code_for_common_punctuation(ch: str, expected: str) -> None:
    assert _char_to_code(ch) == expected


def test_char_to_code_unknown_falls_back_to_char() -> None:
    # No mapping for, say, currency symbols; should return the raw char.
    assert _char_to_code("€") == "€"


def test_metadata_table_has_every_printable_expected_key() -> None:
    required = {"Enter", "Tab", "Escape", "Backspace", "Space", "ArrowUp"}
    assert required.issubset(_KEY_METADATA.keys())
