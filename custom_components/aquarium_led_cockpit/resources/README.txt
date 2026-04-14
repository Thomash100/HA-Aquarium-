Aquarium LED Cockpit exported files
===================================

This folder contains the files exported by the HACS integration.

Blueprint
- /config/blueprints/automation/aquarium_led_cockpit/aquarium_led_tibber_weather_shelly_rgbw.yaml

Dashboard snippets
- /config/aquarium_led_cockpit/dashboard/aquarium_led_status_sensor.yaml
- /config/aquarium_led_cockpit/dashboard/aquarium_led_cockpit_visual_button_card_sensor.yaml
- /config/aquarium_led_cockpit/dashboard/aquarium_led_technikpanel_sensor.yaml

Live status entity
- sensor.aquarium_led_cockpit_status

Automation service
- aquarium_led_cockpit.set_dashboard_status

Notes
- Install custom:button-card through HACS if you want the visual cards.
- Legacy helper and cards are optional and are only exported when enabled in the integration options.
- Repository: https://github.com/Thomash100/HA-Aquarium-

