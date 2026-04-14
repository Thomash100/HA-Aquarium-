# Aquarium LED Cockpit

Aquarium LED Cockpit is a Home Assistant custom integration for aquarium lighting automation with price-aware dimming, weather-based cloud simulation, sunrise/sunset phases, and ready-to-use dashboard views.

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Thomash100&repository=HA-Aquarium-&category=integration)
![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)
![GitHub Release](https://img.shields.io/github/v/release/Thomash100/HA-Aquarium-?sort=semver)
![License](https://img.shields.io/github/license/Thomash100/HA-Aquarium-)

Transform your aquarium lighting into a dynamic day cycle that reacts to the sun, electricity prices, and weather conditions. The integration packages a complete blueprint, exports dashboard cards into the correct Home Assistant folders, and exposes a live status sensor for cockpit-style visualizations.

> Demo media and screenshots can be added here later. The repository is already structured for a polished HACS presentation.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Dashboard Variants](#dashboard-variants)
- [Entities and Services](#entities-and-services)
- [Exported Files](#exported-files)
- [Troubleshooting](#troubleshooting)
- [Repository Structure](#repository-structure)
- [License](#license)

## Features

- Dynamic aquarium LED control for Shelly RGBW lights
- Sunrise and sunset phases based on `sun.sun`
- Daytime cloud simulation with weather-aware dimming
- Tibber spot-price support and generic price entities for other providers
- Optional legacy `input_text` export for older dashboard setups
- Live dashboard entity: `sensor.aquarium_led_cockpit_status`
- Visual dashboard cards for cockpit and technical panel layouts
- One-click export of blueprint and dashboard files into Home Assistant config folders

## Installation

### HACS

1. Add this repository to HACS as a custom repository with category `Integration`.
2. Install `Aquarium LED Cockpit`.
3. Restart Home Assistant.
4. Go to `Settings -> Devices & Services`.
5. Add the `Aquarium LED Cockpit` integration.

### Home Assistant My Link

Use this direct HACS link:

[Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Thomash100&repository=HA-Aquarium-&category=integration)

## Quick Start

1. Install the integration through HACS.
2. Restart Home Assistant.
3. Add the integration in `Settings -> Devices & Services`.
4. Leave `auto_install` enabled to export the included files automatically.
5. Reload blueprints in Home Assistant.
6. Create an automation from the exported aquarium blueprint.
7. Add one of the exported dashboard cards to Lovelace.

After setup, the integration can export:

- the aquarium blueprint to `/config/blueprints/automation/aquarium_led_cockpit/`
- sensor-based dashboard cards to `/config/aquarium_led_cockpit/dashboard/`
- optional legacy helper/card files for older setups

## Dashboard Variants

The integration currently ships with three dashboard snippets:

| Variant | File | Purpose |
| --- | --- | --- |
| Markdown status | `aquarium_led_status_sensor.yaml` | Lightweight status overview without custom cards |
| Visual cockpit | `aquarium_led_cockpit_visual_button_card_sensor.yaml` | Single-card glass cockpit with RGBW, price, weather, and phase status |
| Technical panel | `aquarium_led_technikpanel_sensor.yaml` | Multi-panel control-room view with separate lighting, price, weather, and timing sections |

For the visual variants, install `custom:button-card` through HACS.

## Entities and Services

### Live Entity

| Entity | Description |
| --- | --- |
| `sensor.aquarium_led_cockpit_status` | Live status entity used by the exported dashboard cards |

### Services

#### `aquarium_led_cockpit.install_resources`

Copies the packaged blueprint and dashboard resources into the Home Assistant config directory.

| Field | Required | Description |
| --- | --- | --- |
| `config_entry_id` | No | Optional config entry id if multiple entries exist |
| `install_blueprint` | No | Export the aquarium blueprint |
| `export_dashboard_snippets` | No | Export the sensor-based dashboard snippets |
| `export_legacy_files` | No | Export legacy helper and dashboard variants |
| `overwrite_existing` | No | Replace already existing files |

#### `aquarium_led_cockpit.set_dashboard_status`

Updates the live status sensor from an automation or script.

| Field | Required | Description |
| --- | --- | --- |
| `status_json` | Yes | Compact JSON object with the aquarium lighting status |

## Exported Files

| File | Destination |
| --- | --- |
| `aquarium_led_tibber_weather_shelly_rgbw.yaml` | `/config/blueprints/automation/aquarium_led_cockpit/` |
| `aquarium_led_status_sensor.yaml` | `/config/aquarium_led_cockpit/dashboard/` |
| `aquarium_led_cockpit_visual_button_card_sensor.yaml` | `/config/aquarium_led_cockpit/dashboard/` |
| `aquarium_led_technikpanel_sensor.yaml` | `/config/aquarium_led_cockpit/dashboard/` |
| `aquarium_led_dashboard_status_helper.yaml` | optional legacy export into `/config/packages/` |

## Troubleshooting

### The integration does not show up after HACS installation

- Restart Home Assistant after the HACS install
- Check that the repository category in HACS is `Integration`
- Confirm that `custom_components/aquarium_led_cockpit/` exists in your Home Assistant config

### The config flow fails during setup

- Remove and reinstall the integration from HACS
- Restart Home Assistant fully before retrying
- Check `Settings -> System -> Logs` for the traceback

### Dashboard cards show no data

- Verify that `sensor.aquarium_led_cockpit_status` exists
- Use the exported blueprint or call `aquarium_led_cockpit.set_dashboard_status`
- For visual cards, ensure `custom:button-card` is installed

### Blueprint or dashboard files were not exported

Run the export service manually:

```yaml
service: aquarium_led_cockpit.install_resources
data:
  install_blueprint: true
  export_dashboard_snippets: true
  export_legacy_files: false
  overwrite_existing: false
```

## Repository Structure

- `custom_components/aquarium_led_cockpit/` contains the integration code
- `custom_components/aquarium_led_cockpit/resources/` contains the packaged blueprint and dashboard files
- `.github/workflows/` contains HACS and hassfest validation workflows
- `info.md` is the short HACS-facing repository description

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).