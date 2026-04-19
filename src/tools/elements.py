# element interaction tools - click, type, clear, focus, select, upload

from zendriver import cdp

from src.errors import ElementNotFoundError
from src.tools._shadow_js import (
    CLICK_BY_TEXT_SHADOW_JS,
    CLICK_SHADOW_HOST_JS,
    DESCRIBE_SHADOW_JS,
)
from src.tools.base import ZENDRIVER_ID_ATTR, ToolBase


class ElementTools(ToolBase):
    """tools for interacting with page elements"""

    def _register_tools(self) -> None:
        """register element interaction tools"""
        self._register(self.click)
        self._register(self.click_shadow)
        self._register(self.describe_shadow)
        self._register(self.type_text)
        self._register(self.clear_input)
        self._register(self.focus_element)
        self._register(self.select_option)
        self._register(self.upload_file)

    async def click(self, selector: str | None = None, text: str | None = None) -> str:
        """Click a visible element.

        Accepts a CSS selector, the numeric id from ``get_interaction_tree``
        (e.g. ``"12"`` -> ``[data-zendriver-id="12"]``), or ``text`` to find
        by visible text content.
        """
        if selector:
            selector = self.resolve_selector(selector)

            check = await self.check_visibility(selector)
            if not check["found"]:
                if f"[{ZENDRIVER_ID_ATTR}=" in selector:
                    return "Error: ID not found. The page may have changed. Please run get_interaction_tree() again."
                raise ElementNotFoundError(selector)
            if check.get("hidden"):
                reason = "0x0 rect" if check.get("zero_size") else "display/visibility hidden"
                return f"Error: Element '{selector}' is hidden ({reason}). Cannot click."
            elem = await self.try_select(selector)
            if elem:
                await elem.click()
                return f"Clicked: {selector}"
            raise ElementNotFoundError(selector)
        elif text:
            # Shadow-DOM-aware click: walks light + every open shadow root,
            # picks the tightest text match, climbs/dives to the deepest
            # interactive element (button, role=radio, custom-element
            # inner control) and dispatches a composed click sequence.
            # Design-system pages (e.g. NS.nl, bunq) wrap their real
            # interactive elements multiple shadow roots deep; a plain
            # Element.click() on the outer host never fires the handler.
            import json as _json

            safe_text = _json.dumps(text)
            # Drop ``return`` - a bare top-level return is a SyntaxError in
            # CDP Runtime.evaluate. The completion value of the final
            # expression statement is what we want back.
            result = await self.run_js(
                CLICK_BY_TEXT_SHADOW_JS + f"\nclickByTextShadow({safe_text})\n"
            )
            if not isinstance(result, dict) or not result.get("ok"):
                raise ElementNotFoundError(f"text={text!r}")
            suffix = (
                f" [shadow depth {result['shadow_depth']}]" if result.get("shadow_depth") else ""
            )
            return f"Clicked: {text}{suffix} (<{result['tag']}>)"
        return "Error: Provide selector or text"

    async def click_shadow(self, selector: str, max_depth: int = 6) -> str:
        """Click the deepest interactive element inside a custom element's shadow DOM.

        Use when a page wraps a real ``<button>`` / ``[role="radio"]`` /
        ``[role="checkbox"]`` in one or more open shadow roots
        (``<nes-button>``, ``<sds-radio>``, ``<lion-input>`` and friends).
        ``selector`` should match the outer custom element in the light
        DOM; this tool then recurses through every nested ``shadowRoot``
        up to ``max_depth`` levels and dispatches a composed click
        sequence on the first interactive descendant it finds.

        Returns an error when the host isn't found or no inner interactive
        element lives inside its shadow tree.
        """
        import json as _json

        selector = self.resolve_selector(selector)
        safe_sel = _json.dumps(selector)
        result = await self.run_js(
            CLICK_SHADOW_HOST_JS + f"\nclickShadowHost({safe_sel}, {int(max_depth)})\n"
        )
        if not isinstance(result, dict) or not result.get("ok"):
            reason = result.get("reason") if isinstance(result, dict) else "unknown"
            if reason == "host_not_found":
                raise ElementNotFoundError(selector)
            return f"Error: no interactive element inside {selector} ({reason})"
        tag = result["tag"]
        role = result.get("role")
        role_info = f" role={role}" if role else ""
        return f"Shadow-clicked: <{tag}{role_info}> inside {selector}"

    async def describe_shadow(self, selector: str, max_depth: int = 6) -> dict:
        """Dump a custom element's nested shadow-DOM tree for debugging.

        Returns a condensed JSON tree - each node has ``tag``, ``id``,
        ``role``, ``type``, ``text``, a ``light`` array of light-DOM
        children and a ``shadow`` array for the element's shadowRoot
        children (when open). Use this when ``find_buttons`` /
        ``find_inputs`` aren't surfacing a control you can see on the
        page; the result tells you the exact nested-host path so you
        can target ``click_shadow`` or chain custom queries.
        """
        import json as _json

        selector = self.resolve_selector(selector)
        safe_sel = _json.dumps(selector)
        result = await self.run_js(
            DESCRIBE_SHADOW_JS + f"\ndescribeShadow({safe_sel}, {int(max_depth)})\n"
        )
        if not isinstance(result, dict) or not result.get("ok"):
            raise ElementNotFoundError(selector)
        return {"selector": selector, "tree": result["tree"]}

    async def type_text(self, text: str, selector: str, replace: bool = True) -> str:
        """Focus an element and type ``text`` via CDP Input.insertText.

        By default the field is cleared first (``replace=True``). Set
        ``replace=False`` to append to the existing value.
        """
        selector = self.resolve_selector(selector)

        # Propagate click errors (hidden element, 0x0 rect, not found) so
        # we don't blast insert_text into whatever else holds focus.
        click_result = await self.click(selector)
        if click_result.startswith("Error:"):
            return click_result
        if replace:
            # clear_input uses elem.apply(...) which doesn't move focus, so
            # no need to re-click here; doing so would double-fire click
            # handlers on date-pickers, toggles, etc.
            await self.clear_input(selector)
        await self.session.page.send(cdp.input_.insert_text(text=text))
        return f"Typed {len(text)} char(s) into {selector}"

    async def clear_input(self, selector: str) -> str:
        """Clear an input or contenteditable element via the native setter.

        Uses the same technique React's synthetic-event system expects so
        controlled components actually see the change. Previously we called
        ``document.execCommand`` which is deprecated and invisible to
        React/Vue/Angular state.
        """
        selector = self.resolve_selector(selector)

        elem = await self.get_element(selector)
        await elem.apply(
            """
            (el) => {
                const tag = el.tagName;
                if (tag === 'INPUT' || tag === 'TEXTAREA') {
                    const proto = tag === 'INPUT'
                        ? window.HTMLInputElement.prototype
                        : window.HTMLTextAreaElement.prototype;
                    const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
                    setter.call(el, '');
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                } else if (el.isContentEditable) {
                    el.textContent = '';
                    el.dispatchEvent(new InputEvent('input', { bubbles: true }));
                }
            }
            """
        )
        return f"Cleared: {selector}"

    async def focus_element(self, selector: str) -> str:
        """Focus on an element."""
        selector = self.resolve_selector(selector)
        elem = await self.get_element(selector)
        await elem.focus()
        return f"Focused on: {selector}"

    async def select_option(self, selector: str, value: str) -> str:
        """Select an option from a dropdown."""
        selector = self.resolve_selector(selector)
        await self.get_element(selector)
        safe_sel = self.escape_js_string(selector)
        safe_val = self.escape_js_string(value)
        await self.run_js(f'''
            const select = document.querySelector("{safe_sel}");
            select.value = "{safe_val}";
            select.dispatchEvent(new Event("change", {{ bubbles: true }}));
        ''')
        return f"Selected '{value}' in: {selector}"

    async def upload_file(self, selector: str, file_path: str) -> str:
        """Upload a file to a file input."""
        selector = self.resolve_selector(selector)
        elem = await self.get_element(selector)
        await elem.send_file(file_path)
        return f"Uploaded file '{file_path}' to: {selector}"
