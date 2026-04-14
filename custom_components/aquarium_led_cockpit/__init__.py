"""The Aquarium LED Cockpit integration."""
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
    CONF_EXPORT_DASHBOARD_SNIPPETS,
    CONF_EXPORT_LEGACY_FILES,
    CONF_INSTALL_BLUEPRINT,
    CONF_OVERWRITE_EXISTING,
    CONF_STATUS_JSON,
    DATA_SERVICES_REGISTERED,
    DEFAULT_AUTO_INSTALL,
    DEFAULT_EXPORT_DASHBOARD_SNIPPETS,
    DEFAULT_EXPORT_LEGACY_FILES,
    DEFAULT_INSTALL_BLUEPRINT,
    DEFAULT_OVERWRITE_EXISTING,
    DOMAIN,
    PLATFORMS,
    SERVICE_INSTALL_RESOURCES,
    SERVICE_SET_DASHBOARD_STATUS,
)

_LOGGER = logging.getLogger(__name__)

INSTALL_RESOURCES_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_CONFIG_ENTRY_ID): cv.string,
        vol.Optional(CONF_INSTALL_BLUEPRINT): cv.boolean,
        vol.Optional(CONF_EXPORT_DASHBOARD_SNIPPETS): cv.boolean,
        vol.Optional(CONF_EXPORT_LEGACY_FILES): cv.boolean,
        vol.Optional(CONF_OVERWRITE_EXISTING): cv.boolean,
    }
)

SET_DASHBOARD_STATUS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_STATUS_JSON): cv.string,
    }
)


def _merged_entry_settings(entry: ConfigEntry) -> dict[str, Any]:
    return {**entry.data, **entry.options}


def _resolve_entry(hass: HomeAssistant, entry_id: str | None) -> ConfigEntry:
    entries = hass.config_entries.async_entries(DOMAIN)

    if not entries:
        raise HomeAssistantError("Aquarium LED Cockpit is not configured yet.")

    if entry_id is None:
        if len(entries) == 1:
            return entries[0]
        raise HomeAssistantError("Please provide config_entry_id when multiple entries exist.")

    for entry in entries:
        if entry.entry_id == entry_id:
            return entry

    raise HomeAssistantError(f"Unknown config_entry_id: {entry_id}")


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
        "Aquarium LED Cockpit has exported the selected resources.",
        "",
    ]

    if created:
        lines.append("Created:")
        lines.extend([f"- {item['description']}: {item['target']}" for item in created])
        lines.append("")

    if updated:
        lines.append("Updated:")
        lines.extend([f"- {item['description']}: {item['target']}" for item in updated])
        lines.append("")

    if skipped:
        lines.append("Skipped:")
        lines.extend([f"- {item['description']}: {item['target']}" for item in skipped])
        lines.append("")

    lines.extend(
        [
            "Next steps:",
            "- Reload blueprints if the automation blueprint was exported.",
            "- Add the exported dashboard YAML snippets from /config/aquarium_led_cockpit/dashboard/ to Lovelace.",
            "- Install custom:button-card through HACS if you want the visual cards.",
            "- The live status entity is sensor.aquarium_led_cockpit_status.",
        ]
    )

    persistent_notification.async_create(
        hass,
        "\n".join(lines),
        title="Aquarium LED Cockpit Installation",
        notification_id="aquarium_led_cockpit_installation",
    )


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up services for Aquarium LED Cockpit."""
    from .runtime import async_get_runtime

    await async_get_runtime(hass)
    domain_data = hass.data.setdefault(DOMAIN, {})

    if domain_data.get(DATA_SERVICES_REGISTERED):
        return True

    async def async_handle_install_resources(call: ServiceCall) -> None:
        from .installer import async_install_resources

        entry = _resolve_entry(hass, call.data.get(CONF_CONFIG_ENTRY_ID))
        settings = _merged_entry_settings(entry)

        results = await async_install_resources(
            hass,
            install_blueprint=call.data.get(
                CONF_INSTALL_BLUEPRINT,
                settings.get(CONF_INSTALL_BLUEPRINT, DEFAULT_INSTALL_BLUEPRINT),
            ),
            export_dashboard_snippets=call.data.get(
                CONF_EXPORT_DASHBOARD_SNIPPETS,
                settings.get(
                    CONF_EXPORT_DASHBOARD_SNIPPETS,
                    DEFAULT_EXPORT_DASHBOARD_SNIPPETS,
                ),
            ),
            export_legacy_files=call.data.get(
                CONF_EXPORT_LEGACY_FILES,
                settings.get(CONF_EXPORT_LEGACY_FILES, DEFAULT_EXPORT_LEGACY_FILES),
            ),
            overwrite_existing=call.data.get(
                CONF_OVERWRITE_EXISTING,
                settings.get(CONF_OVERWRITE_EXISTING, DEFAULT_OVERWRITE_EXISTING),
            ),
        )

        await _async_notify_installation(hass, results, automatic=False)

    async def async_handle_set_dashboard_status(call: ServiceCall) -> None:
        from .runtime import async_get_runtime

        runtime = await async_get_runtime(hass)

        try:
            payload = json.loads(call.data[CONF_STATUS_JSON])
        except json.JSONDecodeError as err:
            raise HomeAssistantError("status_json must contain valid JSON.") from err

        if not isinstance(payload, dict):
            raise HomeAssistantError("status_json must decode to a JSON object.")

        await runtime.async_set_status(payload)

    hass.services.async_register(
        DOMAIN,
        SERVICE_INSTALL_RESOURCES,
        async_handle_install_resources,
        schema=INSTALL_RESOURCES_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_DASHBOARD_STATUS,
        async_handle_set_dashboard_status,
        schema=SET_DASHBOARD_STATUS_SCHEMA,
    )
    domain_data[DATA_SERVICES_REGISTERED] = True
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Aquarium LED Cockpit from a config entry."""
    from .installer import async_install_resources
    from .runtime import async_get_runtime

    await async_get_runtime(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    settings = _merged_entry_settings(entry)
    if settings.get(CONF_AUTO_INSTALL, DEFAULT_AUTO_INSTALL):
        results = await async_install_resources(
            hass,
            install_blueprint=settings.get(CONF_INSTALL_BLUEPRINT, DEFAULT_INSTALL_BLUEPRINT),
            export_dashboard_snippets=settings.get(
                CONF_EXPORT_DASHBOARD_SNIPPETS,
                DEFAULT_EXPORT_DASHBOARD_SNIPPETS,
            ),
            export_legacy_files=settings.get(
                CONF_EXPORT_LEGACY_FILES,
                DEFAULT_EXPORT_LEGACY_FILES,
            ),
            overwrite_existing=settings.get(
                CONF_OVERWRITE_EXISTING,
                DEFAULT_OVERWRITE_EXISTING,
            ),
        )
        await _async_notify_installation(hass, results, automatic=True)
        _LOGGER.debug("Automatic resource export finished: %s", results)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Aquarium LED Cockpit."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
