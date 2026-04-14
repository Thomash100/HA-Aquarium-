# Aquarium LED Cockpit

Aquarium LED Cockpit is a HACS-installable Home Assistant custom integration for aquarium lighting automations.
It exports the aquarium LED blueprint into the correct Home Assistant folders, provides ready-to-paste dashboard cards,
and exposes a live status sensor for cockpit views.

Repository: https://github.com/Thomash100/HA-Aquarium-

## Features

- exports the aquarium lighting blueprint into `/config/blueprints/automation/aquarium_led_cockpit/`
- exposes `sensor.aquarium_led_cockpit_status` as the live dashboard entity
- provides `aquarium_led_cockpit.set_dashboard_status` for the automation blueprint
- exports ready-to-use dashboard YAML snippets into `/config/aquarium_led_cockpit/dashboard/`
- can optionally export the old `input_text` helper package and legacy dashboard cards

## HACS installation

1. Add this repository to HACS as a custom repository of type `Integration`.
2. Install `Aquarium LED Cockpit` through HACS.
3. Restart Home Assistant.
4. Add the integration in `Settings -> Devices & Services`.
5. Keep `auto_install` enabled if you want the files to be exported automatically.

## After setup

- reload blueprints in Home Assistant
- import or paste the files from `/config/aquarium_led_cockpit/dashboard/` into your dashboard
- install `button-card` with HACS if you want the visual cards
- use the exported blueprint, which pushes live status into `sensor.aquarium_led_cockpit_status`

## Included files

- Blueprint: `aquarium_led_tibber_weather_shelly_rgbw.yaml`
- Markdown card: `aquarium_led_status_sensor.yaml`
- Visual cockpit card: `aquarium_led_cockpit_visual_button_card_sensor.yaml`
- Technical panel card: `aquarium_led_technikpanel_sensor.yaml`
- Legacy helper package: `aquarium_led_dashboard_status_helper.yaml`

## Repository structure

- `custom_components/aquarium_led_cockpit/` contains the integration code
- `.github/workflows/` contains validation workflows for hassfest and HACS
- `info.md` provides the short HACS information page
- `LICENSE` ships the MIT license for redistribution and reuse

## Notes for publishing

- GitHub topics, repository description and optional brand assets are repository settings outside the files in this repo.
- The HACS validation workflow ignores those external checks so the CI focuses on the files you actually version here.
