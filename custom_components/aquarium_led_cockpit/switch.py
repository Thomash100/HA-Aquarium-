"""Switch platform for Aquarium LED Cockpit."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONTROL_AQUARIUM_PREVIEW,
    CONTROL_ENABLED,
    CONTROL_SIMULATION,
    CONTROL_TIME_LAPSE,
    DOMAIN,
)
from .runtime import AquariumLedCockpitRuntime, async_get_runtime


SWITCHES = (
    (CONTROL_ENABLED, "Steuerung", "mdi:fishbowl-outline"),
    (CONTROL_SIMULATION, "Simulation", "mdi:test-tube"),
    (CONTROL_TIME_LAPSE, "Zeitraffer", "mdi:fast-forward"),
    (
        CONTROL_AQUARIUM_PREVIEW,
        "Zeitraffer am Aquarium",
        "mdi:fishbowl-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches from a config entry."""
    runtime = await async_get_runtime(hass, entry.entry_id)
    async_add_entities(
        [
            AquariumLedCockpitSwitch(runtime, entry, key, name, icon)
            for key, name, icon in SWITCHES
        ],
        True,
    )


class AquariumLedCockpitSwitch(SwitchEntity):
    """Expose an aquarium control switch."""

    _attr_should_poll = False

    def __init__(
        self,
        runtime: AquariumLedCockpitRuntime,
        entry: ConfigEntry,
        key: str,
        name: str,
        icon: str,
    ) -> None:
        self._runtime = runtime
        self._key = key
        self._attr_name = f"{entry.title} {name}"
        self._attr_icon = icon
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Aquarium LED Cockpit",
        )

    @property
    def is_on(self) -> bool:
        """Return switch state."""
        return bool(self._runtime.controls.get(self._key))

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self._runtime.async_set_control(self._key, True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self._runtime.async_set_control(self._key, False)

    async def async_added_to_hass(self) -> None:
        """Subscribe to runtime updates."""
        self.async_on_remove(self._runtime.async_listen(self._handle_status_updated))

    @callback
    def _handle_status_updated(self) -> None:
        """Write the latest state to Home Assistant."""
        self.async_write_ha_state()
