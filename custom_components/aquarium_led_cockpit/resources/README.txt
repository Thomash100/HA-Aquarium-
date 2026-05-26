Exportierte Dateien von Aquarium LED Cockpit
============================================

Dieser Ordner enthaelt nur noch Ressourcen, die von der nativen Integration
wirklich benoetigt werden.

Lovelace-Ressource
- /config/www/aquarium_led_cockpit/aquarium-led-simulator-card.js
- Dashboard-Ressource: /local/aquarium_led_cockpit/aquarium-led-simulator-card.js

Live-Status-Entitaet
- wird aus dem Aquarium-Namen gebildet, zum Beispiel sensor.aquarium_status

Automation-Dienst
- aquarium_led_cockpit.set_dashboard_status

Hinweise
- Blueprint-, Legacy-, Helper- und YAML-Dashboard-Beispieldateien wurden entfernt.
- Die native Integration steuert die Aquarium-LEDs direkt ueber eigene Entitaeten.
- Fuege die Lovelace-Ressource hinzu, wenn du die Simulator-Karte nutzen moechtest.
- Repository: https://github.com/Thomash100/HA-Aquarium-
