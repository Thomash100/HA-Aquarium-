# Aquarium LED Cockpit

Aquarium LED Cockpit ist eine ueber HACS installierbare Home-Assistant-Custom-Integration fuer dynamische Aquarium-Beleuchtung.

Veroeffentlichungskennzeichen: `V260523.001_BETA.00`

Home-Assistant-Manifest-Version: `26.5.23-beta.1`

Die Integration kombiniert:

- sonnenbasierte Sonnenaufgangs- und Sonnenuntergangsphasen
- Tibber oder generische Strompreis-Entitaeten
- wetterabhaengige Dimmung und Wolkensimulation
- Simulationsmodus ohne Lichtbefehle
- Zeitraffer-Simulation zum Testen der Tageslogik
- exportierte Dashboard-Karten fuer eine Cockpit-Ansicht
- eine Live-Entitaet: `sensor.aquarium_led_cockpit_status`

## Installation

1. Fuege dieses Repository in HACS als benutzerdefiniertes Repository mit Kategorie `Integration` hinzu.
2. Installiere `Aquarium LED Cockpit`.
3. Starte Home Assistant neu.
4. Fuege die Integration unter `Einstellungen -> Geraete & Dienste` hinzu.
5. Waehle deine Licht-, Wetter-, Sonnen- und optionalen Preis-Entitaeten aus.

## Enthalten

- Aquarium-Lichtsteuerung direkt in der Integration
- Aquarium-Licht-Blueprint als Kompatibilitaetsweg
- Sensorbasierte Markdown-Dashboard-Karte
- Visuelle Cockpit-Dashboard-Karte
- Technikpanel-Dashboard-Karte
- Optionaler Legacy-Helfer-Export

Repository: https://github.com/Thomash100/HA-Aquarium-
