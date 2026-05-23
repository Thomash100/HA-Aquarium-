"""Sensor platform for Aquarium LED Cockpit."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, STATUS_SENSOR_NAME, STATUS_SENSOR_UNIQUE_ID
from .runtime import AquariumLedCockpitRuntime, async_get_runtime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the status sensor from a config entry."""
    runtime = await async_get_runtime(hass, entry.entry_id)
    async_add_entities([AquariumLedCockpitStatusSensor(runtime, entry)], True)


class AquariumLedCockpitStatusSensor(SensorEntity):
    """Expose the latest aquarium automation status as a sensor."""

    _attr_icon = "mdi:fishbowl"
    _attr_should_poll = False

    def __init__(self, runtime: AquariumLedCockpitRuntime, entry: ConfigEntry) -> None:
        self._runtime = runtime
        self._attr_name = f"{entry.title} Status"
        self._attr_unique_id = f"{STATUS_SENSOR_UNIQUE_ID}_{entry.entry_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title or STATUS_SENSOR_NAME,
            manufacturer="Aquarium LED Cockpit",
        )

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
