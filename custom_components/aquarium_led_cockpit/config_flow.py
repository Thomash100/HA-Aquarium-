"""Config flow for Aquarium LED Cockpit."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_AUTO_INSTALL,
    CONF_BATTERY_FULL_THRESHOLD,
    CONF_BATTERY_SOC_ENTITY,
    CONF_EXPORT_FRONTEND_RESOURCES,
    CONF_NAME,
    CONF_OVERWRITE_EXISTING,
    CONF_PRICE_ENTITY,
    CONF_RGBW_LIGHTS,
    CONF_SUN_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_TRANSITION_SECONDS,
    CONF_WEATHER_ENTITY,
    CONF_WHITE_LIGHTS,
    DEFAULT_AUTO_INSTALL,
    DEFAULT_BATTERY_FULL_THRESHOLD,
    DEFAULT_EXPORT_FRONTEND_RESOURCES,
    DEFAULT_OVERWRITE_EXISTING,
    DEFAULT_SUN_ENTITY,
    DEFAULT_TRANSITION_SECONDS,
    DOMAIN,
)


def _build_schema(defaults: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_NAME,
                default=defaults.get(CONF_NAME, "Aquarium"),
            ): selector.TextSelector(),
            vol.Optional(
                CONF_RGBW_LIGHTS,
                default=defaults.get(CONF_RGBW_LIGHTS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="light", multiple=True)
            ),
            vol.Optional(
                CONF_WHITE_LIGHTS,
                default=defaults.get(CONF_WHITE_LIGHTS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="light", multiple=True)
            ),
            vol.Optional(
                CONF_WEATHER_ENTITY,
                default=defaults.get(CONF_WEATHER_ENTITY, ""),
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="weather")),
            vol.Optional(
                CONF_SUN_ENTITY,
                default=defaults.get(CONF_SUN_ENTITY, DEFAULT_SUN_ENTITY),
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sun")),
            vol.Optional(
                CONF_PRICE_ENTITY,
                default=defaults.get(CONF_PRICE_ENTITY, ""),
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Optional(
                CONF_BATTERY_SOC_ENTITY,
                default=defaults.get(CONF_BATTERY_SOC_ENTITY, ""),
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Optional(
                CONF_SOLAR_POWER_ENTITY,
                default=defaults.get(CONF_SOLAR_POWER_ENTITY, ""),
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(
                CONF_BATTERY_FULL_THRESHOLD,
                default=defaults.get(
                    CONF_BATTERY_FULL_THRESHOLD,
                    DEFAULT_BATTERY_FULL_THRESHOLD,
                ),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=50,
                    max=100,
                    step=1,
                    mode=selector.NumberSelectorMode.SLIDER,
                    unit_of_measurement="%",
                )
            ),
            vol.Required(
                CONF_TRANSITION_SECONDS,
                default=defaults.get(CONF_TRANSITION_SECONDS, DEFAULT_TRANSITION_SECONDS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=1800,
                    step=5,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="s",
                )
            ),
            vol.Required(
                CONF_EXPORT_FRONTEND_RESOURCES,
                default=defaults.get(
                    CONF_EXPORT_FRONTEND_RESOURCES,
                    DEFAULT_EXPORT_FRONTEND_RESOURCES,
                ),
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
            name = str(user_input[CONF_NAME]).strip() or "Aquarium"
            user_input = {**user_input, CONF_NAME: name}
            await self.async_set_unique_id(name)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=name, data=user_input)

        return self.async_show_form(step_id="user", data_schema=_build_schema({}))


class AquariumLedCockpitOptionsFlow(config_entries.OptionsFlow):
    """Handle Aquarium LED Cockpit options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, bool] | None = None):
        """Manage the integration options."""
        if user_input is not None:
            name = str(user_input[CONF_NAME]).strip() or self.config_entry.title or "Aquarium"
            user_input = {**user_input, CONF_NAME: name}
            self.hass.config_entries.async_update_entry(self.config_entry, title=name)
            return self.async_create_entry(title="", data=user_input)

        defaults = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_build_schema(defaults))
