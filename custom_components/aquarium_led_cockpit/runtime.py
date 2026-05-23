"""Runtime state for Aquarium LED Cockpit."""
from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store

from .const import (
    CONF_RGBW_LIGHTS,
    CONF_TRANSITION_SECONDS,
    CONF_WHITE_LIGHTS,
    CONTROL_CLOUD_STRENGTH,
    CONTROL_DAY_BRIGHTNESS,
    CONTROL_ENABLED,
    CONTROL_NIGHT_BRIGHTNESS,
    CONTROL_PRICE_DIMMING,
    CONTROL_SIMULATION,
    CONTROL_SIMULATION_STEP,
    CONTROL_SIMULATION_TIME,
    CONTROL_TIME_LAPSE,
    DATA_RUNTIMES,
    DEFAULT_CLOUD_STRENGTH,
    DEFAULT_DAY_BRIGHTNESS,
    DEFAULT_NIGHT_BRIGHTNESS,
    DEFAULT_PRICE_DIMMING,
    DEFAULT_SIMULATION_STEP,
    DEFAULT_SIMULATION_TIME,
    DEFAULT_TRANSITION_SECONDS,
    DOMAIN,
    STORAGE_KEY_PREFIX,
    STORAGE_VERSION,
)
from .engine import calculate_target

DEFAULT_CONTROLS = {
    CONTROL_ENABLED: False,
    CONTROL_SIMULATION: True,
    CONTROL_TIME_LAPSE: False,
    CONTROL_DAY_BRIGHTNESS: DEFAULT_DAY_BRIGHTNESS,
    CONTROL_NIGHT_BRIGHTNESS: DEFAULT_NIGHT_BRIGHTNESS,
    CONTROL_PRICE_DIMMING: DEFAULT_PRICE_DIMMING,
    CONTROL_CLOUD_STRENGTH: DEFAULT_CLOUD_STRENGTH,
    CONTROL_SIMULATION_TIME: DEFAULT_SIMULATION_TIME,
    CONTROL_SIMULATION_STEP: DEFAULT_SIMULATION_STEP,
}


class AquariumLedCockpitRuntime:
    """Keep the latest dashboard payload and notify listeners."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self.entry_title = "Aquarium"
        self._status: dict[str, Any] = {}
        self._controls: dict[str, Any] = dict(DEFAULT_CONTROLS)
        self._listeners: list[Callable[[], None]] = []
        self._store: Store[dict[str, Any]] = Store(
            hass,
            STORAGE_VERSION,
            f"{STORAGE_KEY_PREFIX}_{entry_id}",
        )
        self._settings: dict[str, Any] = {}
        self._unsub_interval: Callable[[], None] | None = None

    @property
    def status(self) -> dict[str, Any]:
        """Return the latest stored status payload."""
        return self._status

    @property
    def controls(self) -> dict[str, Any]:
        """Return current UI controls."""
        return self._controls

    async def async_load(self) -> None:
        """Load the last stored payload from disk."""
        stored = await self._store.async_load()
        if isinstance(stored, dict):
            self._status = stored.get("status", stored) if "status" in stored else stored
            stored_controls = stored.get("controls") if "controls" in stored else None
            if isinstance(stored_controls, dict):
                self._controls.update(stored_controls)

    async def async_set_status(self, status: dict[str, Any]) -> None:
        """Persist the latest dashboard status."""
        self._status = dict(status)
        await self._async_save()
        for listener in list(self._listeners):
            listener()

    async def async_set_control(self, key: str, value: Any) -> None:
        """Persist and apply a UI control value."""
        self._controls[key] = value
        await self.async_update_target(apply_lights=True)

    async def async_configure_entry(self, entry: ConfigEntry) -> None:
        """Configure the runtime from a config entry."""
        self._settings = {**entry.data, **entry.options}
        self.entry_title = entry.title
        await self.async_update_target(apply_lights=False)
        if self._unsub_interval is None:
            self._unsub_interval = async_track_time_interval(
                self.hass,
                self._async_interval_update,
                timedelta(minutes=1),
            )

    async def async_unload(self) -> None:
        """Stop runtime callbacks."""
        if self._unsub_interval is not None:
            self._unsub_interval()
            self._unsub_interval = None

    async def _async_interval_update(self, _now) -> None:
        """Update target and advance time-lapse state."""
        if self._controls.get(CONTROL_TIME_LAPSE):
            current = int(self._controls.get(CONTROL_SIMULATION_TIME, DEFAULT_SIMULATION_TIME))
            step = int(self._controls.get(CONTROL_SIMULATION_STEP, DEFAULT_SIMULATION_STEP))
            self._controls[CONTROL_SIMULATION_TIME] = (current + step) % 1440
        await self.async_update_target(apply_lights=True)

    async def async_update_target(self, *, apply_lights: bool) -> None:
        """Calculate the target and optionally apply it to configured lights."""
        target = calculate_target(self.hass, self._settings, self._controls)
        await self.async_set_status(target.status)

        if not apply_lights:
            return
        if not self._controls.get(CONTROL_ENABLED):
            return
        if target.status.get("simulation"):
            return

        rgbw_lights = self._normalize_entities(self._settings.get(CONF_RGBW_LIGHTS))
        white_lights = self._normalize_entities(self._settings.get(CONF_WHITE_LIGHTS))
        transition = self._settings.get(CONF_TRANSITION_SECONDS, DEFAULT_TRANSITION_SECONDS)
        if rgbw_lights and target.brightness_pct > 0:
            await self.hass.services.async_call(
                "light",
                "turn_on",
                {
                    ATTR_ENTITY_ID: rgbw_lights,
                    "brightness_pct": target.brightness_pct,
                    "rgbw_color": list(target.rgbw),
                    "transition": transition,
                },
                blocking=False,
            )
        elif rgbw_lights:
            await self.hass.services.async_call(
                "light",
                "turn_off",
                {ATTR_ENTITY_ID: rgbw_lights, "transition": transition},
                blocking=False,
            )

        white_pct = int(target.status.get("white_pct") or 0)
        if white_lights and white_pct > 0:
            await self.hass.services.async_call(
                "light",
                "turn_on",
                {ATTR_ENTITY_ID: white_lights, "brightness_pct": white_pct, "transition": transition},
                blocking=False,
            )
        elif white_lights:
            await self.hass.services.async_call(
                "light",
                "turn_off",
                {ATTR_ENTITY_ID: white_lights, "transition": transition},
                blocking=False,
            )

    async def _async_save(self) -> None:
        await self._store.async_save({"status": self._status, "controls": self._controls})

    @staticmethod
    def _normalize_entities(value: Any) -> list[str]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value if item]
        return []

    def async_listen(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Register a callback for status updates."""
        self._listeners.append(listener)

        def _unsubscribe() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return _unsubscribe


async def async_get_runtime(hass: HomeAssistant, entry_id: str) -> AquariumLedCockpitRuntime:
    """Return the runtime for a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    runtimes = domain_data.setdefault(DATA_RUNTIMES, {})
    runtime = runtimes.get(entry_id)
    if runtime is None:
        runtime = AquariumLedCockpitRuntime(hass, entry_id)
        await runtime.async_load()
        runtimes[entry_id] = runtime
    return runtime


def async_remove_runtime(hass: HomeAssistant, entry_id: str) -> None:
    """Remove a runtime from Home Assistant data."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    runtimes = domain_data.setdefault(DATA_RUNTIMES, {})
    runtimes.pop(entry_id, None)
