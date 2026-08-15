"""Number platform for Aquarium LED Cockpit."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONTROL_CLOUD_STRENGTH,
    CONTROL_DAY_BRIGHTNESS,
    CONTROL_NIGHT_BRIGHTNESS,
    CONTROL_PRICE_DIMMING,
    CONTROL_SIMULATION_TIME,
    CONTROL_TIME_LAPSE_DURATION,
    DOMAIN,
)
from .runtime import AquariumLedCockpitRuntime, async_get_runtime
from .time_lapse import (
    MAX_TIME_LAPSE_DURATION_MINUTES,
    MIN_TIME_LAPSE_DURATION_MINUTES,
)


@dataclass(frozen=True)
class NumberDescription:
    """Description for a runtime number."""

    key: str
    name: str
    icon: str
    minimum: float
    maximum: float
    step: float
    unit: str | None
    mode: NumberMode


NUMBERS = (
    NumberDescription(
        CONTROL_DAY_BRIGHTNESS,
        "Taghelligkeit",
        "mdi:weather-sunny",
        1,
        100,
        1,
        PERCENTAGE,
        NumberMode.SLIDER,
    ),
    NumberDescription(
        CONTROL_NIGHT_BRIGHTNESS,
        "Nachtlicht",
        "mdi:weather-night",
        1,
        30,
        1,
        PERCENTAGE,
        NumberMode.SLIDER,
    ),
    NumberDescription(
        CONTROL_PRICE_DIMMING,
        "Preisdimmung",
        "mdi:cash-remove",
        0,
        90,
        1,
        PERCENTAGE,
        NumberMode.SLIDER,
    ),
    NumberDescription(
        CONTROL_CLOUD_STRENGTH,
        "Wolkenstaerke",
        "mdi:weather-cloudy-arrow-right",
        0,
        100,
        1,
        PERCENTAGE,
        NumberMode.SLIDER,
    ),
    NumberDescription(
        CONTROL_SIMULATION_TIME,
        "Simulationszeit",
        "mdi:clock-fast",
        0,
        1439,
        1,
        UnitOfTime.MINUTES,
        NumberMode.BOX,
    ),
    NumberDescription(
        CONTROL_TIME_LAPSE_DURATION,
        "Zeitraffer-Dauer",
        "mdi:timer-fast",
        MIN_TIME_LAPSE_DURATION_MINUTES,
        MAX_TIME_LAPSE_DURATION_MINUTES,
        1,
        UnitOfTime.MINUTES,
        NumberMode.SLIDER,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up numbers from a config entry."""
    runtime = await async_get_runtime(hass, entry.entry_id)
    async_add_entities(
        [
            AquariumLedCockpitNumber(runtime, entry, description)
            for description in NUMBERS
        ],
        True,
    )


class AquariumLedCockpitNumber(NumberEntity):
    """Expose a runtime number control."""

    _attr_should_poll = False

    def __init__(
        self,
        runtime: AquariumLedCockpitRuntime,
        entry: ConfigEntry,
        description: NumberDescription,
    ) -> None:
        self._runtime = runtime
        self._description = description
        self._attr_name = f"{entry.title} {description.name}"
        self._attr_icon = description.icon
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{description.key}"
        self._attr_native_min_value = description.minimum
        self._attr_native_max_value = description.maximum
        self._attr_native_step = description.step
        self._attr_native_unit_of_measurement = description.unit
        self._attr_mode = description.mode
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Aquarium LED Cockpit",
        )

    @property
    def native_value(self) -> float:
        """Return the current number value."""
        return float(self._runtime.controls.get(self._description.key, self._description.minimum))

    async def async_set_native_value(self, value: float) -> None:
        """Set number value."""
        clipped = max(self._description.minimum, min(self._description.maximum, value))
        await self._runtime.async_set_control(self._description.key, clipped)

    async def async_added_to_hass(self) -> None:
        """Subscribe to runtime updates."""
        self.async_on_remove(self._runtime.async_listen(self._handle_status_updated))

    @callback
    def _handle_status_updated(self) -> None:
        """Write the latest state to Home Assistant."""
        self.async_write_ha_state()
