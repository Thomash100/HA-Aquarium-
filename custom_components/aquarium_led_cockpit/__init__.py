"""The Aquarium LED Cockpit integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up Aquarium LED Cockpit."""
    from .integration import async_setup_integration

    return await async_setup_integration(hass, config)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Aquarium LED Cockpit from a config entry."""
    from .integration import async_setup_entry_integration

    return await async_setup_entry_integration(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Aquarium LED Cockpit."""
    from .integration import async_unload_entry_integration

    return await async_unload_entry_integration(hass, entry)