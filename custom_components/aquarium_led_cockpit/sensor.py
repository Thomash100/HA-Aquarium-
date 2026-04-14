"""Sensor platform for Aquarium LED Cockpit."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import STATUS_SENSOR_NAME, STATUS_SENSOR_UNIQUE_ID
from .runtime import AquariumLedCockpitRuntime, async_get_runtime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the status sensor from a config entry."""
    runtime = await async_get_runtime(hass)
    async_add_entities([AquariumLedCockpitStatusSensor(runtime)], True)


class AquariumLedCockpitStatusSensor(SensorEntity):
    """Expose the latest aquarium automation status as a sensor."""

    _attr_name = STATUS_SENSOR_NAME
    _attr_unique_id = STATUS_SENSOR_UNIQUE_ID
    _attr_icon = "mdi:fishbowl"
    _attr_should_poll = False

    def __init__(self, runtime: AquariumLedCockpitRuntime) -> None:
        self._runtime = runtime

    @property
    def native_value(self) -> str:
        """Return the primary sensor state."""
        return str(self._runtime.status.get("phase") or "idle")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the latest payload as sensor attributes."""
        return dict(self._runtime.status)

    async def async_added_to_hass(self) -> None:
        """Subscribe to runtime updates."""
        self.async_on_remove(self._runtime.async_listen(self._handle_status_updated))

    @callback
    def _handle_status_updated(self) -> None:
        """Write the latest state to Home Assistant."""
        self.async_write_ha_state()
