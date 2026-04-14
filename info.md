# Aquarium LED Cockpit

Aquarium LED Cockpit is a HACS-installable Home Assistant custom integration.
It packages the aquarium lighting blueprint, exports ready-to-use dashboard cards,
and provides a live status sensor for dashboards.

## Highlights

- Dynamic aquarium lighting blueprint for Shelly RGBW
- Supports Tibber and generic electricity price entities
- Weather-aware dimming and cloud simulation
- Sunrise and sunset phases based on `sun.sun`
- Visual dashboard cards for cockpit and technical panel layouts
- Live status sensor: `sensor.aquarium_led_cockpit_status`

## Installation

1. Add the repository to HACS as a custom repository with category `Integration`.
2. Install `Aquarium LED Cockpit`.
3. Restart Home Assistant.
4. Add the integration under `Settings -> Devices & Services`.
5. Let the integration export the blueprint and dashboard snippets.

## Repository

- GitHub: https://github.com/Thomash100/HA-Aquarium-
- Documentation and issues are handled in this repository.
