"""Stealth tools: Cloudflare solver and identity overrides.

These rely on CDP-level primitives that WebDriver-based automation either
can't reach or reveals itself through. Everything here is optional - none of
it is needed for basic page interaction.
"""

from __future__ import annotations

from zendriver import cdp
from zendriver.core.cloudflare import (
    cf_is_interactive_challenge_present,
    verify_cf,
)

from src.errors import CloudflareChallengeError
from src.tools.base import ToolBase


class StealthTools(ToolBase):
    """Tools for evading bot detection and overriding browser identity."""

    def _register_tools(self) -> None:
        # Cloudflare solver clicks up to `timeout` seconds; give it room.
        self._register(self.bypass_cloudflare, timeout=120)
        self._register(self.is_cloudflare_challenge_present, timeout=15)
        self._register(self.set_user_agent)
        self._register(self.clear_user_agent)
        self._register(self.set_locale)
        self._register(self.set_timezone)
        self._register(self.set_geolocation)

    async def bypass_cloudflare(
        self,
        timeout: float = 15.0,
        click_delay: float = 5.0,
    ) -> str:
        """Solve a Cloudflare interactive (Turnstile) challenge on the current page.

        Waits up to ``timeout`` seconds for the challenge iframe and then clicks
        the checkbox every ``click_delay`` seconds until the input disappears
        or gets a value. Raises TimeoutError if the challenge cannot be solved
        in time.
        """
        try:
            await verify_cf(
                self.session.page,
                click_delay=click_delay,
                timeout=timeout,
            )
        except TimeoutError as exc:
            raise CloudflareChallengeError(str(exc)) from exc
        return "Cloudflare challenge solved"

    async def is_cloudflare_challenge_present(self, timeout: float = 5.0) -> bool:
        """Report whether a Cloudflare interactive challenge is visible.

        Fast probe - use before ``bypass_cloudflare`` to skip the click cycle
        when the page already passed.
        """
        return await cf_is_interactive_challenge_present(self.session.page, timeout=timeout)

    async def set_user_agent(
        self,
        user_agent: str,
        accept_language: str | None = None,
        platform: str | None = None,
    ) -> str:
        """Override User-Agent, Accept-Language, and navigator.platform.

        Applies to every subsequent request on the current tab until
        ``clear_user_agent`` is called or the tab closes. ``platform`` should
        match the UA (e.g. ``"Win32"`` for a Windows UA).
        """
        await self.session.page.send(
            cdp.network.set_user_agent_override(
                user_agent=user_agent,
                accept_language=accept_language,
                platform=platform,
            )
        )
        return f"User-Agent overridden: {user_agent}"

    async def clear_user_agent(self) -> str:
        """Remove a previous User-Agent override and restore the default."""
        await self.session.page.send(cdp.network.set_user_agent_override(user_agent=""))
        return "User-Agent override cleared"

    async def set_locale(self, locale: str) -> str:
        """Override the browser locale (ICU C-style, e.g. ``nl_NL``, ``en_US``).

        Affects navigator.language, Intl APIs, and Accept-Language defaults.
        Pass an empty string to restore the system locale.
        """
        await self.session.page.send(cdp.emulation.set_locale_override(locale=locale or None))
        return f"Locale set to: {locale or '(system default)'}"

    async def set_timezone(self, timezone_id: str) -> str:
        """Override the IANA timezone (e.g. ``Europe/Amsterdam``, ``America/New_York``).

        Pass an empty string to restore the system timezone.
        """
        await self.session.page.send(cdp.emulation.set_timezone_override(timezone_id=timezone_id))
        return f"Timezone set to: {timezone_id or '(system default)'}"

    async def set_geolocation(
        self,
        latitude: float,
        longitude: float,
        accuracy: float = 100.0,
    ) -> str:
        """Override the browser's geolocation. Accuracy is in metres."""
        await self.session.page.send(
            cdp.emulation.set_geolocation_override(
                latitude=latitude,
                longitude=longitude,
                accuracy=accuracy,
            )
        )
        return f"Geolocation set to: lat={latitude}, lon={longitude}"
