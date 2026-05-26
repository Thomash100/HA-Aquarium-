"""Runtime setup logic for Aquarium LED Cockpit."""
from __future__ import annotations

import json
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_AUTO_INSTALL,
    CONF_CONFIG_ENTRY_ID,
    CONF_EXPORT_FRONTEND_RESOURCES,
    CONF_OVERWRITE_EXISTING,
    CONF_STATUS_JSON,
    DATA_SERVICES_REGISTERED,
    DEFAULT_AUTO_INSTALL,
    DEFAULT_EXPORT_FRONTEND_RESOURCES,
    DEFAULT_OVERWRITE_EXISTING,
    DOMAIN,
    PLATFORMS,
    SERVICE_INSTALL_RESOURCES,
    SERVICE_SET_DASHBOARD_STATUS,
)

_LOGGER = logging.getLogger(__name__)


def _merged_entry_settings(entry: ConfigEntry) -> dict[str, Any]:
    return {**entry.data, **entry.options}


def _resolve_entry(hass: HomeAssistant, entry_id: str | None) -> ConfigEntry:
    entries = hass.config_entries.async_entries(DOMAIN)

    if not entries:
        raise HomeAssistantError("Aquarium LED Cockpit ist noch nicht konfiguriert.")

    if entry_id is None:
        if len(entries) == 1:
            return entries[0]
        raise HomeAssistantError("Bitte config_entry_id angeben, wenn mehrere Eintraege existieren.")

    for entry in entries:
        if entry.entry_id == entry_id:
            return entry

    raise HomeAssistantError(f"Unbekannte config_entry_id: {entry_id}")


async def _async_notify_installation(
    hass: HomeAssistant,
    results: list[dict[str, Any]],
    *,
    automatic: bool,
) -> None:
    created = [item for item in results if item["status"] == "created"]
    updated = [item for item in results if item["status"] == "updated"]
    skipped = [item for item in results if item["status"] == "skipped"]

    if automatic and not created and not updated:
        return

    lines = [
        "Aquarium LED Cockpit hat die ausgewaehlten Ressourcen exportiert.",
        "",
    ]

    if created:
        lines.append("Erstellt:")
        lines.extend([f"- {item['description']}: {item['target']}" for item in created])
        lines.append("")

    if updated:
        lines.append("Aktualisiert:")
        lines.extend([f"- {item['description']}: {item['target']}" for item in updated])
        lines.append("")

    if skipped:
        lines.append("Uebersprungen:")
        lines.extend([f"- {item['description']}: {item['target']}" for item in skipped])
        lines.append("")

    lines.extend(
        [
            "Naechste Schritte:",
            "- Lovelace-Ressource /local/aquarium_led_cockpit/aquarium-led-simulator-card.js hinzufuegen, wenn die Simulator-Karte genutzt wird.",
            "- Die Live-Status-Entitaet wird aus dem Aquarium-Namen gebildet, zum Beispiel sensor.aquarium_status.",
        ]
    )

    persistent_notification.async_create(
        hass,
        "\n".join(lines),
        title="Aquarium LED Cockpit Installation",
        notification_id="aquarium_led_cockpit_installation",
    )


async def async_setup_integration(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up services for Aquarium LED Cockpit."""
    from .installer import async_install_resources
    from .runtime import async_get_runtime

    install_resources_schema = vol.Schema(
        {
            vol.Optional(CONF_CONFIG_ENTRY_ID): cv.string,
            vol.Optional(CONF_EXPORT_FRONTEND_RESOURCES): cv.boolean,
            vol.Optional(CONF_OVERWRITE_EXISTING): cv.boolean,
        }
    )
    set_dashboard_status_schema = vol.Schema(
        {
            vol.Optional(CONF_CONFIG_ENTRY_ID): cv.string,
            vol.Required(CONF_STATUS_JSON): cv.string,
        }
    )

    domain_data = hass.data.setdefault(DOMAIN, {})

    if domain_data.get(DATA_SERVICES_REGISTERED):
        return True

    async def async_handle_install_resources(call: ServiceCall) -> None:
        entry = _resolve_entry(hass, call.data.get(CONF_CONFIG_ENTRY_ID))
        settings = _merged_entry_settings(entry)

        results = await async_install_resources(
            hass,
            export_frontend_resources=call.data.get(
                CONF_EXPORT_FRONTEND_RESOURCES,
                settings.get(
                    CONF_EXPORT_FRONTEND_RESOURCES,
                    DEFAULT_EXPORT_FRONTEND_RESOURCES,
                ),
            ),
            overwrite_existing=call.data.get(
                CONF_OVERWRITE_EXISTING,
                settings.get(CONF_OVERWRITE_EXISTING, DEFAULT_OVERWRITE_EXISTING),
            ),
        )

        await _async_notify_installation(hass, results, automatic=False)

    async def async_handle_set_dashboard_status(call: ServiceCall) -> None:
        entry = _resolve_entry(hass, call.data.get(CONF_CONFIG_ENTRY_ID))
        runtime = await async_get_runtime(hass, entry.entry_id)

        try:
            payload = json.loads(call.data[CONF_STATUS_JSON])
        except json.JSONDecodeError as err:
            raise HomeAssistantError("status_json muss gueltiges JSON enthalten.") from err

        if not isinstance(payload, dict):
            raise HomeAssistantError("status_json muss ein JSON-Objekt ergeben.")

        await runtime.async_set_status(payload)

    hass.services.async_register(
        DOMAIN,
        SERVICE_INSTALL_RESOURCES,
        async_handle_install_resources,
        schema=install_resources_schema,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_DASHBOARD_STATUS,
        async_handle_set_dashboard_status,
        schema=set_dashboard_status_schema,
    )
    domain_data[DATA_SERVICES_REGISTERED] = True
    return True


async def async_setup_entry_integration(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Aquarium LED Cockpit from a config entry."""
    from .installer import async_install_resources
    from .runtime import async_get_runtime

    runtime = await async_get_runtime(hass, entry.entry_id)
    await runtime.async_configure_entry(entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    settings = _merged_entry_settings(entry)
    if settings.get(CONF_AUTO_INSTALL, DEFAULT_AUTO_INSTALL):
        results = await async_install_resources(
            hass,
            export_frontend_resources=settings.get(
                CONF_EXPORT_FRONTEND_RESOURCES,
                DEFAULT_EXPORT_FRONTEND_RESOURCES,
            ),
            overwrite_existing=settings.get(
                CONF_OVERWRITE_EXISTING,
                DEFAULT_OVERWRITE_EXISTING,
            ),
        )
        await _async_notify_installation(hass, results, automatic=True)
        _LOGGER.debug("Automatic resource export finished: %s", results)

    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry_integration(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Aquarium LED Cockpit."""
    from .runtime import async_get_runtime, async_remove_runtime

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        runtime = await async_get_runtime(hass, entry.entry_id)
        await runtime.async_unload()
        async_remove_runtime(hass, entry.entry_id)
    return unload_ok
