"""Config flow for Aquarium LED Cockpit."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_AUTO_INSTALL,
    CONF_EXPORT_DASHBOARD_SNIPPETS,
    CONF_EXPORT_LEGACY_FILES,
    CONF_INSTALL_BLUEPRINT,
    CONF_OVERWRITE_EXISTING,
    DEFAULT_AUTO_INSTALL,
    DEFAULT_EXPORT_DASHBOARD_SNIPPETS,
    DEFAULT_EXPORT_LEGACY_FILES,
    DEFAULT_INSTALL_BLUEPRINT,
    DEFAULT_OVERWRITE_EXISTING,
    DOMAIN,
)


def _build_schema(defaults: dict[str, bool]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_INSTALL_BLUEPRINT,
                default=defaults.get(CONF_INSTALL_BLUEPRINT, DEFAULT_INSTALL_BLUEPRINT),
            ): bool,
            vol.Required(
                CONF_EXPORT_DASHBOARD_SNIPPETS,
                default=defaults.get(
                    CONF_EXPORT_DASHBOARD_SNIPPETS,
                    DEFAULT_EXPORT_DASHBOARD_SNIPPETS,
                ),
            ): bool,
            vol.Required(
                CONF_EXPORT_LEGACY_FILES,
                default=defaults.get(CONF_EXPORT_LEGACY_FILES, DEFAULT_EXPORT_LEGACY_FILES),
            ): bool,
            vol.Required(
                CONF_OVERWRITE_EXISTING,
                default=defaults.get(CONF_OVERWRITE_EXISTING, DEFAULT_OVERWRITE_EXISTING),
            ): bool,
            vol.Required(
                CONF_AUTO_INSTALL,
                default=defaults.get(CONF_AUTO_INSTALL, DEFAULT_AUTO_INSTALL),
            ): bool,
        }
    )


class AquariumLedCockpitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aquarium LED Cockpit."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return AquariumLedCockpitOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, bool] | None = None):
        """Handle the initial config step."""
        if user_input is not None:
            return self.async_create_entry(title="Aquarium LED Cockpit", data=user_input)

        return self.async_show_form(step_id="user", data_schema=_build_schema({}))


class AquariumLedCockpitOptionsFlow(config_entries.OptionsFlow):
    """Handle Aquarium LED Cockpit options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, bool] | None = None):
        """Manage the integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        defaults = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_build_schema(defaults))