# Aquarium LED Cockpit

Aquarium LED Cockpit is a HACS-installable Home Assistant custom integration for dynamic aquarium lighting.

It combines:

- sun-based sunrise and sunset phases
- Tibber or generic electricity price inputs
- weather-aware dimming and cloud simulation
- exported dashboard cards for a cockpit-style UI
- a live entity: `sensor.aquarium_led_cockpit_status`

## Install

1. Add this repository to HACS as a custom repository with category `Integration`.
2. Install `Aquarium LED Cockpit`.
3. Restart Home Assistant.
4. Add the integration in `Settings -> Devices & Services`.
5. Let the integration export the blueprint and dashboard files.

## Included

- Aquarium lighting blueprint
- Sensor-based markdown dashboard card
- Visual cockpit dashboard card
- Technical panel dashboard card
- Optional legacy helper export

Repository: https://github.com/Thomash100/HA-Aquarium-