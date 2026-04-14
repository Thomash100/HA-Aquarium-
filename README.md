# Aquarium LED Cockpit

A HACS installable Home Assistant integration that exports the aquarium LED blueprint and ready to paste dashboard cards into the correct config folders.

## What this integration does

- installs the aquarium lighting blueprint into `/config/blueprints/automation/aquarium_led_cockpit/`
- exposes `sensor.aquarium_led_cockpit_status` for the live dashboard state
- provides the service `aquarium_led_cockpit.set_dashboard_status` for the automation blueprint
- exports ready to use dashboard YAML snippets into `/config/aquarium_led_cockpit/dashboard/`
- can optionally export the old `input_text` helper package and legacy dashboard cards

## HACS installation

1. Add this repository to HACS as a custom repository of type `Integration`.
2. Install `Aquarium LED Cockpit` through HACS.
3. Restart Home Assistant.
4. Add the integration in `Settings -> Devices & Services`.
5. Keep `auto install` enabled if you want the files to be exported automatically.

## After setup

- reload blueprints in Home Assistant
- import or paste the files from `/config/aquarium_led_cockpit/dashboard/` into your dashboard
- install `button-card` with HACS if you want the visual cards
- use the exported blueprint, which now pushes live status into `sensor.aquarium_led_cockpit_status`

## Included files

- Blueprint: `aquarium_led_tibber_weather_shelly_rgbw.yaml`
- Markdown card: `aquarium_led_status_sensor.yaml`
- Visual cockpit card: `aquarium_led_cockpit_visual_button_card_sensor.yaml`
- Technical panel card: `aquarium_led_technikpanel_sensor.yaml`

## Publishing note

Repository: https://github.com/Thomash100/HA-Aquarium-

