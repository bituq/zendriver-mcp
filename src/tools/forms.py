# form and input tools - fill form, submit, keyboard, mouse
import json

from zendriver import cdp

from src.tools.base import ToolBase

# Windows virtual-key codes for the named keys. Values sourced from
# Chromium's ui/events/keycodes/dom/keycode_converter_data.inc.
_KEY_METADATA: dict[str, tuple[int, str]] = {
    "Enter": (13, "Enter"),
    "Tab": (9, "Tab"),
    "Escape": (27, "Escape"),
    "Backspace": (8, "Backspace"),
    "Delete": (46, "Delete"),
    "ArrowUp": (38, "ArrowUp"),
    "ArrowDown": (40, "ArrowDown"),
    "ArrowLeft": (37, "ArrowLeft"),
    "ArrowRight": (39, "ArrowRight"),
    "Space": (32, "Space"),
    " ": (32, "Space"),
    "Home": (36, "Home"),
    "End": (35, "End"),
    "PageUp": (33, "PageUp"),
    "PageDown": (34, "PageDown"),
}


class FormTools(ToolBase):
    """tools for forms and input handling"""

    def _register_tools(self) -> None:
        """register form and input tools"""
        self._register(self.fill_form)
        self._register(self.submit_form)
        self._register(self.press_key)
        self._register(self.press_enter)
        self._register(self.mouse_click)

    async def fill_form(self, form_data: str) -> str:
        """Fill multiple form fields. Pass JSON like ``{"#email": "x@y.com"}``.

        Reports which selectors succeeded and which were missing so the
        caller can tell partial fills from full ones. Fields are cleared
        before typing so values don't concatenate with existing content.
        """
        data = json.loads(form_data)
        filled: list[str] = []
        missing: list[str] = []

        for selector, value in data.items():
            elem = await self.try_select(selector)
            if elem is None:
                missing.append(selector)
                continue
            await elem.clear_input()
            await elem.send_keys(str(value))
            filled.append(selector)

        if missing:
            return (
                f"Filled {len(filled)} field(s): {', '.join(filled) or '(none)'}; "
                f"missing {len(missing)}: {', '.join(missing)}"
            )
        return f"Filled {len(filled)} field(s): {', '.join(filled)}"

    async def submit_form(self, selector: str = "form") -> str:
        """Submit a form, honouring framework-level submit listeners.

        Uses ``form.requestSubmit()`` so React/Vue/Formik ``onSubmit``
        handlers fire and HTML validation runs, falling back to a bubbling
        ``submit`` event and finally ``form.submit()`` for ancient pages.
        Returns an error if the selector matches no form.
        """
        import json as _json

        sel_json = _json.dumps(selector)
        result = await self.run_js(
            f"""
            (function() {{
                const form = document.querySelector({sel_json});
                if (!form) return 'missing';
                if (typeof form.requestSubmit === 'function') {{
                    form.requestSubmit();
                    return 'requestSubmit';
                }}
                const ev = new Event('submit', {{ bubbles: true, cancelable: true }});
                const proceed = form.dispatchEvent(ev);
                if (proceed) form.submit();
                return proceed ? 'dispatched' : 'prevented';
            }})()
            """
        )
        if result == "missing":
            return f"Error: no form matched selector {selector!r}"
        return f"Form submitted: {selector} ({result})"

    async def press_key(self, key: str, selector: str | None = None) -> str:
        """Press a keyboard key via CDP ``Input.dispatchKeyEvent``.

        Uses real browser key events, not synthetic JS dispatch - so native
        form-submit semantics, browser shortcuts, and IME all behave as
        they would with a human keyboard. When ``selector`` is given we
        focus that element first.

        Recognised names: ``Enter``, ``Tab``, ``Escape``, ``Backspace``,
        ``Delete``, ``ArrowUp/Down/Left/Right``, ``Space``, ``Home``, ``End``,
        ``PageUp``, ``PageDown``. Any single character (e.g. ``"a"``) is also
        accepted.
        """
        if selector:
            await self.focus_selector(selector)

        meta = _KEY_METADATA.get(key)
        tab = self.session.page
        if meta is not None:
            code, key_name = meta
            await tab.send(
                cdp.input_.dispatch_key_event(
                    type_="rawKeyDown",
                    key=key_name,
                    code=key_name,
                    windows_virtual_key_code=code,
                    native_virtual_key_code=code,
                )
            )
            await tab.send(
                cdp.input_.dispatch_key_event(
                    type_="keyUp",
                    key=key_name,
                    code=key_name,
                    windows_virtual_key_code=code,
                    native_virtual_key_code=code,
                )
            )
        elif len(key) == 1:
            await tab.send(
                cdp.input_.dispatch_key_event(
                    type_="keyDown",
                    text=key,
                    unmodified_text=key,
                    key=key,
                    code=f"Key{key.upper()}" if key.isalpha() else key,
                )
            )
            await tab.send(
                cdp.input_.dispatch_key_event(
                    type_="keyUp",
                    key=key,
                    code=f"Key{key.upper()}" if key.isalpha() else key,
                )
            )
        else:
            return f"Error: unknown key {key!r}"

        return f"Pressed key: {key}" + (f" on {selector}" if selector else "")

    async def focus_selector(self, selector: str) -> None:
        """Focus an element via JS (helper, no separate MCP registration)."""
        elem = await self.get_element(selector)
        await elem.focus()

    async def press_enter(self, selector: str | None = None) -> str:
        """Press Enter key - convenience wrapper for press_key('Enter')."""
        return await self.press_key("Enter", selector)

    async def mouse_click(self, x: int, y: int) -> str:
        """Click at specific coordinates."""
        await self.session.page.mouse_click(x, y)
        return f"Clicked at ({x}, {y})"
