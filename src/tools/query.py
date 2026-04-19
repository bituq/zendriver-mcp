# element query tools - find element, find all, get text, get attribute, find buttons

from src.tools._shadow_js import COLLECT_INTERACTIVES_JS
from src.tools.base import ToolBase


class QueryTools(ToolBase):
    """tools for querying and inspecting elements"""

    def _register_tools(self) -> None:
        """register element query tools"""
        self._register(self.find_element)
        self._register(self.find_all_elements)
        self._register(self.get_element_text)
        self._register(self.get_element_attribute)
        self._register(self.find_buttons)
        self._register(self.find_inputs)

    async def find_element(self, selector: str | None = None, text: str | None = None) -> str:
        """Find an element and return information about it.

        Provides helpful suggestions if element is not found.
        """
        page = self.session.page

        if selector:
            try:
                elem = await page.select(selector, timeout=2)
            except Exception:
                elem = None

            if elem is None:
                # provide helpful suggestions
                suggestions = await self.run_js("""
                    (function() {
                        const found = [];
                        const ce = document.querySelector('[contenteditable="true"]');
                        if (ce) found.push({ sel: '[contenteditable="true"]', tag: ce.tagName });
                        const tb = document.querySelector('[role="textbox"]');
                        if (tb) found.push({ sel: '[role="textbox"]', tag: tb.tagName });
                        const ta = document.querySelector('textarea');
                        if (ta) found.push({ sel: 'textarea', tag: 'TEXTAREA' });
                        const inp = document.querySelector('input:not([type="hidden"])');
                        if (inp) found.push({ sel: 'input', tag: 'INPUT', type: inp.type });
                        const btn = document.querySelector('button');
                        if (btn) found.push({ sel: 'button', tag: 'BUTTON' });
                        return found.slice(0, 5);
                    })()
                """)

                msg = f"Element not found: {selector}"
                if suggestions:
                    suggestions_text = ", ".join([s["sel"] for s in suggestions])
                    msg += f"\nAvailable interactive elements: {suggestions_text}"
                return msg

            tag = getattr(elem, "tag_name", "unknown")
            text_content = getattr(elem, "text", "") or ""

            # get additional useful info
            safe_sel = self.escape_js_string(selector)
            extra_info = await self.run_js(f'''
                (function() {{
                    const el = document.querySelector("{safe_sel}");
                    if (!el) return {{}};
                    const style = window.getComputedStyle(el);
                    return {{
                        visible: style.display !== "none" && style.visibility !== "hidden",
                        editable: el.isContentEditable || el.tagName === "INPUT" || el.tagName === "TEXTAREA",
                        clickable: el.tagName === "BUTTON" || el.tagName === "A" || el.onclick !== null
                    }};
                }})()
            ''')

            visibility = "visible" if extra_info.get("visible", True) else "HIDDEN"
            return f"Found <{tag}> ({visibility}): {text_content[:200] if text_content else '(no text)'}"

        elif text:
            elem = await page.find(text, best_match=True)
            if elem is None:
                return f"Element not found with text: {text}"
            tag = getattr(elem, "tag_name", "unknown")
            return f"Found <{tag}> matching: {text}"

        return "Error: Provide selector or text"

    async def find_all_elements(self, selector: str, limit: int = 20) -> str:
        """Find all elements matching a selector. Returns quickly on no match.

        ``limit`` caps the number of summary rows; the total count is always
        accurate. Zendriver's ``select_all`` raises ``TimeoutError`` after
        ~10s on zero matches, which we catch and translate to a clean
        "no elements found" message.
        """
        import asyncio as _asyncio

        try:
            elems = await self.session.page.select_all(selector, timeout=2)
        except _asyncio.TimeoutError:
            return f"No elements found: {selector}"
        if not elems:
            return f"No elements found: {selector}"

        total = len(elems)
        shown = min(total, limit)
        results = []
        for i, elem in enumerate(elems[:shown]):
            tag = getattr(elem, "tag_name", "unknown")
            text = (getattr(elem, "text", "") or "")[:50]
            results.append(f"{i + 1}. <{tag}> {text}")

        suffix = f" (showing {shown} of {total})" if total > shown else ""
        return f"Found {total} element(s){suffix}:\n" + "\n".join(results)

    async def get_element_text(self, selector: str) -> str:
        """Get the text content of an element."""
        elem = await self.get_element(selector)
        text = getattr(elem, "text", "") or ""
        return text if text else "(empty)"

    async def get_element_attribute(self, selector: str, attribute: str) -> str:
        """Get an attribute value from an element."""
        elem = await self.get_element(selector)
        attrs = getattr(elem, "attrs", {})
        value = attrs.get(attribute) if attrs else None
        return str(value) if value else "(not set)"

    async def find_buttons(self, filter_text: str | None = None) -> str:
        """Find all clickable elements on the page - including shadow DOM.

        Walks both the light DOM and every open shadow root, so buttons
        hidden inside custom elements like ``<nes-button>`` or
        ``<sds-cta>`` show up. Recognises native tags (button, a, input,
        summary) plus ARIA roles (button, link, checkbox, radio, switch,
        menuitem, tab, option, treeitem) and cursor=pointer elements
        with an onclick handler. Each entry shows the host's CSS
        selector; for shadow-wrapped buttons use ``click_shadow`` to
        reach the inner interactive element.
        """
        import json as _json

        needle = _json.dumps(filter_text or "")
        buttons = await self.run_js(
            COLLECT_INTERACTIVES_JS + f"\nreturn collectButtons({needle});\n"
        )

        if not buttons:
            return "No buttons found" + (f" matching '{filter_text}'" if filter_text else "")

        lines = [f"Found {len(buttons)} button(s):"]
        for i, btn in enumerate(buttons):
            marker = " (custom)" if btn.get("custom") else ""
            lines.append(
                f"  {i + 1}. [{btn['type']}]{marker} {btn['description'][:60]} -> {btn['selector']}"
            )

        return "\n".join(lines)

    async def find_inputs(self, filter_type: str | None = None) -> str:
        """Find all input fields on the page - including shadow DOM.

        Walks both the light DOM and every open shadow root. Recognises
        ``<input>``, ``<textarea>``, ``role=textbox/searchbox/combobox``,
        ``[contenteditable="true"]`` and custom elements whose tag name
        suggests an input (contains "input" or "field"). ``filter_type``
        is a case-insensitive substring match against the input's type
        attribute or ARIA role.
        """
        import json as _json

        filt = _json.dumps(filter_type or "")
        inputs = await self.run_js(COLLECT_INTERACTIVES_JS + f"\nreturn collectInputs({filt});\n")

        if not inputs:
            return "No input fields found" + (f" of type '{filter_type}'" if filter_type else "")

        lines = [f"Found {len(inputs)} input(s):"]
        for i, inp in enumerate(inputs):
            marker = " (custom)" if inp.get("custom") else ""
            lines.append(
                f"  {i + 1}. [{inp['type']}]{marker} {inp['description'][:60]} -> {inp['selector']}"
            )

        return "\n".join(lines)
