"""Runtime state for Aquarium LED Cockpit."""
from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store

from .const import (
    CONF_RGBW_LIGHTS,
    CONF_TRANSITION_SECONDS,
    CONF_WHITE_LIGHTS,
    CONTROL_AQUARIUM_PREVIEW,
    CONTROL_CLOUD_STRENGTH,
    CONTROL_DAY_BRIGHTNESS,
    CONTROL_ENABLED,
    CONTROL_NIGHT_BRIGHTNESS,
    CONTROL_PRICE_DIMMING,
    CONTROL_SIMULATION,
    CONTROL_SIMULATION_TIME,
    CONTROL_TIME_LAPSE_DURATION,
    CONTROL_TIME_LAPSE,
    DATA_RUNTIMES,
    DEFAULT_CLOUD_STRENGTH,
    DEFAULT_DAY_BRIGHTNESS,
    DEFAULT_NIGHT_BRIGHTNESS,
    DEFAULT_PRICE_DIMMING,
    DEFAULT_SIMULATION_TIME,
    DEFAULT_TRANSITION_SECONDS,
    DOMAIN,
    STORAGE_KEY_PREFIX,
    STORAGE_VERSION,
)
from .engine import calculate_target
from .time_lapse import (
    DEFAULT_TIME_LAPSE_DURATION_MINUTES,
    advance_time_lapse_position,
    is_time_lapse_cycle_complete,
    normalize_time_lapse_duration,
)

DEFAULT_CONTROLS = {
    CONTROL_ENABLED: False,
    CONTROL_SIMULATION: True,
    CONTROL_TIME_LAPSE: False,
    CONTROL_AQUARIUM_PREVIEW: False,
    CONTROL_DAY_BRIGHTNESS: DEFAULT_DAY_BRIGHTNESS,
    CONTROL_NIGHT_BRIGHTNESS: DEFAULT_NIGHT_BRIGHTNESS,
    CONTROL_PRICE_DIMMING: DEFAULT_PRICE_DIMMING,
    CONTROL_CLOUD_STRENGTH: DEFAULT_CLOUD_STRENGTH,
    CONTROL_SIMULATION_TIME: DEFAULT_SIMULATION_TIME,
    CONTROL_TIME_LAPSE_DURATION: DEFAULT_TIME_LAPSE_DURATION_MINUTES,
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
        self._unsub_time_lapse_interval: Callable[[], None] | None = None
        self._time_lapse_position: float | None = None
        self._time_lapse_last_tick: float | None = None
        self._preview_started_at: float | None = None
        self._preview_previous_time_lapse = False
        self._preview_previous_simulation_time = DEFAULT_SIMULATION_TIME
        self._preview_light_states: dict[str, dict[str, Any]] = {}

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
        self._controls[CONTROL_TIME_LAPSE_DURATION] = normalize_time_lapse_duration(
            self._controls.get(CONTROL_TIME_LAPSE_DURATION)
        )
        # A physical preview is deliberately transient and never resumes after a reload.
        self._controls[CONTROL_AQUARIUM_PREVIEW] = False

    async def async_set_status(
        self,
        status: dict[str, Any],
        *,
        persist: bool = True,
    ) -> None:
        """Persist the latest dashboard status."""
        self._status = dict(status)
        if persist:
            await self._async_save()
        for listener in list(self._listeners):
            listener()

    async def async_set_control(self, key: str, value: Any) -> None:
        """Persist and apply a UI control value."""
        if key == CONTROL_AQUARIUM_PREVIEW:
            if bool(value):
                await self._async_start_aquarium_preview()
            else:
                await self._async_stop_aquarium_preview()
            return
        if (
            key == CONTROL_ENABLED
            and not bool(value)
            and self._controls.get(CONTROL_AQUARIUM_PREVIEW)
        ):
            await self._async_stop_aquarium_preview()
        if (
            key == CONTROL_TIME_LAPSE
            and not bool(value)
            and self._controls.get(CONTROL_AQUARIUM_PREVIEW)
        ):
            await self._async_stop_aquarium_preview()
        if key == CONTROL_TIME_LAPSE_DURATION:
            value = normalize_time_lapse_duration(value)
        if key == CONTROL_SIMULATION_TIME and self._controls.get(CONTROL_TIME_LAPSE):
            self._time_lapse_position = float(value)
            self._time_lapse_last_tick = self.hass.loop.time()
        if key == CONTROL_TIME_LAPSE:
            if bool(value) and not self._controls.get(CONTROL_TIME_LAPSE):
                self._time_lapse_position = float(
                    self._controls.get(CONTROL_SIMULATION_TIME, DEFAULT_SIMULATION_TIME)
                )
                self._time_lapse_last_tick = self.hass.loop.time()
            elif not bool(value):
                self._time_lapse_position = None
                self._time_lapse_last_tick = None
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
        if self._unsub_time_lapse_interval is None:
            self._unsub_time_lapse_interval = async_track_time_interval(
                self.hass,
                self._async_time_lapse_update,
                timedelta(seconds=1),
            )

    async def async_unload(self) -> None:
        """Stop runtime callbacks."""
        if self._controls.get(CONTROL_AQUARIUM_PREVIEW):
            await self._async_stop_aquarium_preview()
        if self._unsub_interval is not None:
            self._unsub_interval()
            self._unsub_interval = None
        if self._unsub_time_lapse_interval is not None:
            self._unsub_time_lapse_interval()
            self._unsub_time_lapse_interval = None
        self._time_lapse_position = None
        self._time_lapse_last_tick = None

    async def _async_start_aquarium_preview(self) -> None:
        """Run one complete time-lapse cycle on the configured physical lights."""
        if self._controls.get(CONTROL_AQUARIUM_PREVIEW):
            return
        if not self._controls.get(CONTROL_ENABLED):
            raise HomeAssistantError(
                "Bitte zuerst die Aquarium-LED-Steuerung einschalten."
            )

        light_states = self._snapshot_configured_lights()
        if not light_states:
            raise HomeAssistantError(
                "Fuer die Aquarium-Vorschau sind keine erreichbaren Leuchten konfiguriert."
            )

        self._preview_previous_time_lapse = bool(
            self._controls.get(CONTROL_TIME_LAPSE)
        )
        self._preview_previous_simulation_time = int(
            self._controls.get(CONTROL_SIMULATION_TIME, DEFAULT_SIMULATION_TIME)
        )
        self._preview_light_states = light_states
        self._controls[CONTROL_AQUARIUM_PREVIEW] = True
        self._controls[CONTROL_TIME_LAPSE] = True
        self._controls[CONTROL_SIMULATION_TIME] = 0
        self._time_lapse_position = 0.0
        self._time_lapse_last_tick = self.hass.loop.time()
        self._preview_started_at = self._time_lapse_last_tick
        await self.async_update_target(apply_lights=True, persist=False)

    async def _async_stop_aquarium_preview(self) -> None:
        """Stop the physical preview and restore its captured light states."""
        if not self._controls.get(CONTROL_AQUARIUM_PREVIEW):
            return

        self._controls[CONTROL_AQUARIUM_PREVIEW] = False
        self._controls[CONTROL_TIME_LAPSE] = self._preview_previous_time_lapse
        self._controls[CONTROL_SIMULATION_TIME] = self._preview_previous_simulation_time
        if self._preview_previous_time_lapse:
            self._time_lapse_position = float(self._preview_previous_simulation_time)
            self._time_lapse_last_tick = self.hass.loop.time()
        else:
            self._time_lapse_position = None
            self._time_lapse_last_tick = None
        self._preview_started_at = None

        light_states = self._preview_light_states
        self._preview_light_states = {}
        await self._async_restore_light_states(light_states)
        await self.async_update_target(apply_lights=False)

    async def _async_interval_update(self, _now) -> None:
        """Update the live target once per minute."""
        if self._controls.get(CONTROL_TIME_LAPSE):
            return
        await self.async_update_target(apply_lights=True)

    async def _async_time_lapse_update(self, _now) -> None:
        """Advance a complete simulated day in the configured 1-10 minutes."""
        if not self._controls.get(CONTROL_TIME_LAPSE):
            return

        now_tick = self.hass.loop.time()
        if self._time_lapse_position is None:
            self._time_lapse_position = float(
                self._controls.get(CONTROL_SIMULATION_TIME, DEFAULT_SIMULATION_TIME)
            )
        if self._time_lapse_last_tick is None:
            self._time_lapse_last_tick = now_tick
        elapsed_seconds = now_tick - self._time_lapse_last_tick
        self._time_lapse_last_tick = now_tick

        if (
            self._controls.get(CONTROL_AQUARIUM_PREVIEW)
            and self._preview_started_at is not None
            and is_time_lapse_cycle_complete(
                now_tick - self._preview_started_at,
                self._controls.get(CONTROL_TIME_LAPSE_DURATION),
            )
        ):
            await self._async_stop_aquarium_preview()
            return

        self._time_lapse_position = advance_time_lapse_position(
            self._time_lapse_position,
            elapsed_seconds,
            self._controls.get(CONTROL_TIME_LAPSE_DURATION),
        )
        self._controls[CONTROL_SIMULATION_TIME] = int(self._time_lapse_position)
        await self.async_update_target(apply_lights=True, persist=False)

    async def async_update_target(
        self,
        *,
        apply_lights: bool,
        persist: bool = True,
    ) -> None:
        """Calculate the target and optionally apply it to configured lights."""
        target = calculate_target(self.hass, self._settings, self._controls)
        await self.async_set_status(target.status, persist=persist)

        if not apply_lights:
            return
        if not self._controls.get(CONTROL_ENABLED):
            return
        aquarium_preview = bool(self._controls.get(CONTROL_AQUARIUM_PREVIEW))
        if target.status.get("simulation") and not aquarium_preview:
            return

        rgbw_lights = self._normalize_entities(self._settings.get(CONF_RGBW_LIGHTS))
        white_lights = self._normalize_entities(self._settings.get(CONF_WHITE_LIGHTS))
        transition = self._settings.get(CONF_TRANSITION_SECONDS, DEFAULT_TRANSITION_SECONDS)
        if aquarium_preview:
            transition = min(max(float(transition), 0), 1)
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

    def _snapshot_configured_lights(self) -> dict[str, dict[str, Any]]:
        """Capture all configured lights before a physical preview starts."""
        entities = [
            *self._normalize_entities(self._settings.get(CONF_RGBW_LIGHTS)),
            *self._normalize_entities(self._settings.get(CONF_WHITE_LIGHTS)),
        ]
        snapshots: dict[str, dict[str, Any]] = {}
        for entity_id in dict.fromkeys(entities):
            state = self.hass.states.get(entity_id)
            if state is None or state.state in {"unknown", "unavailable"}:
                continue
            snapshots[entity_id] = {
                "state": state.state,
                "attributes": dict(state.attributes),
            }
        return snapshots

    async def _async_restore_light_states(
        self,
        snapshots: dict[str, dict[str, Any]],
    ) -> None:
        """Restore the exact on/off, brightness, and color state after preview."""
        for entity_id, snapshot in snapshots.items():
            if snapshot.get("state") != "on":
                await self.hass.services.async_call(
                    "light",
                    "turn_off",
                    {ATTR_ENTITY_ID: entity_id, "transition": 1},
                    blocking=False,
                )
                continue

            attributes = snapshot.get("attributes", {})
            service_data: dict[str, Any] = {
                ATTR_ENTITY_ID: entity_id,
                "transition": 1,
            }
            brightness = attributes.get("brightness")
            if brightness is not None:
                service_data["brightness"] = brightness
            for color_attribute in (
                "rgbw_color",
                "rgbww_color",
                "rgb_color",
                "hs_color",
                "xy_color",
                "color_temp_kelvin",
            ):
                color_value = attributes.get(color_attribute)
                if color_value is not None:
                    service_data[color_attribute] = color_value
                    break
            await self.hass.services.async_call(
                "light",
                "turn_on",
                service_data,
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
