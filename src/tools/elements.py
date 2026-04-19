# element interaction tools - click, type, clear, focus, select, upload

from zendriver import cdp

from src.errors import ElementNotFoundError
from src.tools.base import ToolBase


class ElementTools(ToolBase):
    """tools for interacting with page elements"""

    def _register_tools(self) -> None:
        """register element interaction tools"""
        self._register(self.click)
        self._register(self.type_text)
        self._register(self.clear_input)
        self._register(self.focus_element)
        self._register(self.select_option)
        self._register(self.upload_file)

    async def click(self, selector: str | None = None, text: str | None = None) -> str:
        """Click a visible element by CSS selector, numeric ID (from get_interaction_tree), or text content."""
        if selector:
            if selector.isdigit():
                selector = f'[data-zendriver-id="{selector}"]'

            check = await self.check_visibility(selector)
            if not check["found"]:
                if "[data-zendriver-id=" in selector:
                    return "Error: ID not found. The page may have changed. Please run get_interaction_tree() again."
                raise ElementNotFoundError(selector)
            if check.get("hidden"):
                return f"Error: Element '{selector}' is hidden. Cannot click."
            elem = await self.try_select(selector)
            if elem:
                await elem.click()
                return f"Clicked: {selector}"
            raise ElementNotFoundError(selector)
        elif text:
            elem = await self.get_element_by_text(text)
            await elem.click()
            return f"Clicked: {text}"
        return "Error: Provide selector or text"

    async def type_text(self, text: str, selector: str, replace: bool = True) -> str:
        """Focus an element and type ``text`` via CDP Input.insertText.

        By default the field is cleared first (``replace=True``). Set
        ``replace=False`` to append to the existing value - useful for
        adding to a partially-filled input without retyping it.
        """
        if selector.isdigit():
            selector = f'[data-zendriver-id="{selector}"]'

        await self.click(selector)
        if replace:
            await self.clear_input(selector)
            # Re-focus after clearing; click() above already did.
            await self.click(selector)
        await self.session.page.send(cdp.input_.insert_text(text=text))
        return f"Typed {len(text)} char(s) into {selector}"

    async def clear_input(self, selector: str) -> str:
        """Clear an input or contenteditable element via the native setter.

        Uses the same technique React's synthetic-event system expects so
        controlled components actually see the change. Previously we called
        ``document.execCommand`` which is deprecated and invisible to
        React/Vue/Angular state.
        """
        if selector.isdigit():
            selector = f'[data-zendriver-id="{selector}"]'

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
        if selector.isdigit():
            selector = f'[data-zendriver-id="{selector}"]'

        elem = await self.get_element(selector)
        await elem.focus()
        return f"Focused on: {selector}"

    async def select_option(self, selector: str, value: str) -> str:
        """Select an option from a dropdown."""
        if selector.isdigit():
            selector = f'[data-zendriver-id="{selector}"]'

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
        if selector.isdigit():
            selector = f'[data-zendriver-id="{selector}"]'

        elem = await self.get_element(selector)
        await elem.send_file(file_path)
        return f"Uploaded file '{file_path}' to: {selector}"
