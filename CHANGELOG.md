# Changelog

## V26.05.19.003_BETA.00

Release management for HACS-style update dialogs.

- Adds an automated GitHub Release workflow for version tags.
- Adds release notes generation from this changelog.
- Keeps semantic Home Assistant manifest versions separate from the visible release label.

## V26.05.19.002_BETA.00

UI-driven aquarium light control inspired by Adaptive Lighting.

- Adds setup options for RGBW lights, optional white channels, weather, sun, price entity, and transition time.
- Adds switch entities for control, simulation, and time-lapse mode.
- Adds number entities for brightness, price dimming, cloud strength, simulation time, and time-lapse speed.
- Adds an internal Python calculation engine for phase, brightness, RGBW, weather, cloud, and price factors.

## V26.05.19.001_BETA.00

Blueprint and dashboard foundation.

- Adds the HACS custom integration skeleton.
- Adds the live cockpit status sensor.
- Exports blueprint, helper package, and dashboard snippets.
- Fixes Home Assistant manifest version compatibility.
