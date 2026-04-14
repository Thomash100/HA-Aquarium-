"""Runtime state for Aquarium LED Cockpit."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DATA_RUNTIME, DOMAIN, STORAGE_KEY, STORAGE_VERSION


class AquariumLedCockpitRuntime:
    """Keep the latest dashboard payload and notify listeners."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._status: dict[str, Any] = {}
        self._listeners: list[Callable[[], None]] = []
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)

    @property
    def status(self) -> dict[str, Any]:
        """Return the latest stored status payload."""
        return self._status

    async def async_load(self) -> None:
        """Load the last stored payload from disk."""
        stored = await self._store.async_load()
        if isinstance(stored, dict):
            self._status = stored

    async def async_set_status(self, status: dict[str, Any]) -> None:
        """Persist the latest dashboard status."""
        self._status = dict(status)
        await self._store.async_save(self._status)
        for listener in list(self._listeners):
            listener()

    def async_listen(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Register a callback for status updates."""
        self._listeners.append(listener)

        def _unsubscribe() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return _unsubscribe


async def async_get_runtime(hass: HomeAssistant) -> AquariumLedCockpitRuntime:
    """Return the shared integration runtime."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    runtime = domain_data.get(DATA_RUNTIME)
    if runtime is None:
        runtime = AquariumLedCockpitRuntime(hass)
        await runtime.async_load()
        domain_data[DATA_RUNTIME] = runtime
    return runtime
