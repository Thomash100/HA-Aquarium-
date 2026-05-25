Exportierte Dateien von Aquarium LED Cockpit
============================================

Dieser Ordner enthaelt die Dateien, die von der HACS-Integration exportiert werden.

Blueprint
- /config/blueprints/automation/aquarium_led_cockpit/aquarium_led_tibber_weather_shelly_rgbw.yaml

Dashboard-Snippets
- /config/aquarium_led_cockpit/dashboard/<aquarium>/aquarium_led_status_sensor.yaml
- /config/aquarium_led_cockpit/dashboard/<aquarium>/aquarium_led_cockpit_visual_button_card_sensor.yaml
- /config/aquarium_led_cockpit/dashboard/<aquarium>/aquarium_led_technikpanel_sensor.yaml
- /config/aquarium_led_cockpit/dashboard/<aquarium>/aquarium_led_controls_panel.yaml
- /config/aquarium_led_cockpit/dashboard/<aquarium>/aquarium_led_power_price_24h.yaml
- /config/aquarium_led_cockpit/dashboard/<aquarium>/aquarium_led_simulator_card.yaml

Lovelace-Ressource
- /config/www/aquarium_led_cockpit/aquarium-led-simulator-card.js
- Dashboard-Ressource: /local/aquarium_led_cockpit/aquarium-led-simulator-card.js

Dashboard-Helfer
- /config/packages/aquarium_led_cockpit_<aquarium>_controls.yaml

Live-Status-Entitaet
- wird aus dem Aquarium-Namen gebildet, zum Beispiel sensor.aquarium_status

Automation-Dienst
- aquarium_led_cockpit.set_dashboard_status

Hinweise
- Installiere custom:button-card ueber HACS, wenn du die visuellen Karten nutzen moechtest.
- Fuege die Lovelace-Ressource hinzu, wenn du die Simulator-Karte nutzen moechtest.
- Exportiere die Ressourcen pro Aquarium erneut, damit die Entity-IDs in den Snippets zum Aquarium-Namen passen.
- Alte globale Helper wie input_boolean.aquarium_led_simulation_mode sind nur noch Legacy. Neue Helper werden pro Aquarium benannt.
- Aktiviere Home-Assistant-Packages, wenn die exportierten Dashboard-Helfer geladen werden sollen.
- Der Simulationshelfer laesst die Blueprint Statuswerte berechnen, ohne Lichtbefehle zu senden.
- Legacy-Helfer und Legacy-Karten sind optional und werden nur exportiert, wenn sie in den Integrationsoptionen aktiviert sind.
- Repository: https://github.com/Thomash100/HA-Aquarium-
