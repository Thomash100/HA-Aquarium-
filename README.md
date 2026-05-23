# Aquarium LED Cockpit

Aquarium LED Cockpit is a Home Assistant custom integration for aquarium lighting automation with price-aware dimming, weather-based cloud simulation, sunrise/sunset phases, and ready-to-use dashboard views.

Release label: `V260523.000_BETA.00`

Home Assistant manifest version: `26.5.23-beta.0`

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Thomash100&repository=HA-Aquarium-&category=integration)
![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)
![GitHub Release](https://img.shields.io/github/v/release/Thomash100/HA-Aquarium-?sort=semver)
![License](https://img.shields.io/github/license/Thomash100/HA-Aquarium-)

Transform your aquarium lighting into a dynamic day cycle that reacts to the sun, electricity prices, and weather conditions. The integration can now be configured directly in Home Assistant, exposes control entities for everyday use, packages a complete blueprint as a compatibility path, exports dashboard cards, and exposes a live status sensor for cockpit-style visualizations.

> Demo media and screenshots can be added here later. The repository is already structured for a polished HACS presentation.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Dashboard Variants](#dashboard-variants)
- [Entities and Services](#entities-and-services)
- [Release History](#release-history)
- [Versioning](#versioning)
- [Exported Files](#exported-files)
- [Troubleshooting](#troubleshooting)
- [Repository Structure](#repository-structure)
- [License](#license)

## Features

- Dynamic aquarium LED control for Shelly RGBW lights
- UI-based setup for RGBW lights, optional white channels, weather, sun, price entity, and transition time
- Built-in switch and number entities for normal operation, safe simulation, and time-lapse testing
- Sunrise and sunset phases based on `sun.sun`
- Daytime cloud simulation with weather-aware dimming
- Simulation mode that updates the cockpit status without sending light commands
- Tibber spot-price support and generic price entities for other providers
- Price-aware dimming where cheap-hour bonus is limited to genuinely low-price ranges
- Optional legacy `input_text` export for older dashboard setups
- Live dashboard entity: `sensor.aquarium_led_cockpit_status`
- Visual dashboard cards for cockpit and technical panel layouts
- One-click export of blueprint and dashboard files into Home Assistant config folders for legacy/manual workflows

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
4. Select your RGBW lights and optional entities in the setup form.
5. Use the created `switch.aquarium_led_steuerung`, simulation switches, and number entities from Home Assistant.
6. Leave `auto_install` enabled if you also want the bundled blueprint and dashboard snippets exported.
7. Add one of the exported dashboard cards to Lovelace if you want a cockpit view.

After setup, the integration can export:

- the aquarium blueprint to `/config/blueprints/automation/aquarium_led_cockpit/`
- sensor-based dashboard cards to `/config/aquarium_led_cockpit/dashboard/`
- dashboard control helpers to `/config/packages/aquarium_led_cockpit_controls.yaml`
- optional legacy helper/card files for older setups

The helper package requires Home Assistant packages to be enabled, for example
`homeassistant: packages: !include_dir_named packages` in `configuration.yaml`.

## Dashboard Variants

The integration currently ships with five dashboard snippets:

| Variant | File | Purpose |
| --- | --- | --- |
| Markdown status | `aquarium_led_status_sensor.yaml` | Lightweight status overview without custom cards |
| Visual cockpit | `aquarium_led_cockpit_visual_button_card_sensor.yaml` | Single-card glass cockpit with RGBW, price, weather, and phase status |
| Technical panel | `aquarium_led_technikpanel_sensor.yaml` | Multi-panel control-room view with separate lighting, price, weather, and timing sections |
| Controls panel | `aquarium_led_controls_panel.yaml` | Entity controls for brightness, cloud strength, maintenance, simulation, and manual RGBW |
| 24h status | `aquarium_led_power_price_24h.yaml` | 24h history card using the built-in cockpit status sensor, ready for optional power and price sensors |

For the visual variants, install `custom:button-card` through HACS.

## Entities and Services

### Live Entity

| Entity | Description |
| --- | --- |
| `sensor.aquarium_led_cockpit_status` | Live status entity used by the exported dashboard cards |
| `switch.aquarium_led_steuerung` | Enables direct light control from the integration |
| `switch.aquarium_led_simulation` | Calculates status without sending light commands |
| `switch.aquarium_led_zeitraffer` | Runs a safe time-lapse simulation without sending light commands |
| `number.aquarium_led_simulationszeit` | Simulated minute of day, where `360` means `06:00` |
| `number.aquarium_led_zeitraffer_schritt` | Minutes added to the simulated time on each real minute tick |

### Time-Lapse Simulation

Turn on the time-lapse switch to test a full day without touching the real
lights. The integration uses the simulation-time number as the clock, writes the
calculated phase, brightness and RGBW values to
`sensor.aquarium_led_cockpit_status`, then advances the simulated time by the
time-lapse step once per real minute.

## Release History

Releases are published from version tags and documented in `CHANGELOG.md`, so
HACS can show selectable versions with release notes in the update dialog.

## Versioning

Visible release labels use `VYYMMDD.NNN_BETA.xx` while the project is in beta.
`YYMMDD` is the release date for fundamental changes, `NNN` is the adjustment
index for compatible follow-up changes on that release line, and `xx` is the
beta iteration. Once the release line is stable, the `_BETA.xx` suffix is
removed. Home Assistant still receives a compatible manifest version such as
`26.5.23-beta.0`.

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
| `aquarium_led_controls_panel.yaml` | `/config/aquarium_led_cockpit/dashboard/` |
| `aquarium_led_power_price_24h.yaml` | `/config/aquarium_led_cockpit/dashboard/` |
| `aquarium_led_cockpit_controls.yaml` | `/config/packages/` |
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
<!-- SYSTEMMEDIA_LEGAL_START -->
## Rechtliche Hinweise

- Impressum: https://systemmedia.de/impressum/
- Datenschutz / DSGVO-Hinweise: https://systemmedia.de/datenschutz/
- Nutzungsbedingungen und Haftungsausschluss: https://systemmedia.de/nutzungsbedingungen/

Dieses Repository enthält, sofern nicht ausdrücklich anders gekennzeichnet, Test-, Entwicklungs-, Demonstrations- oder Evaluierungsinhalte. Nutzung auf eigene Verantwortung.

Soweit eine `LICENSE`-Datei vorhanden ist, gelten die dort genannten Lizenzbedingungen für die eingeräumten Nutzungsrechte. Ergänzend gelten die Status-, Gewährleistungs- und Haftungshinweise in `LEGAL.md`.
<!-- SYSTEMMEDIA_LEGAL_END -->
