# Aquarium LED Cockpit

Aquarium LED Cockpit ist eine ueber HACS installierbare Home-Assistant-Custom-Integration fuer dynamische Aquarium-Beleuchtung.

Veroeffentlichungskennzeichen: `V260523.007_BETA.00`

Home-Assistant-Manifest-Version: `26.5.23-beta.7`

Die Integration kombiniert:

- sonnenbasierte Sonnenaufgangs- und Sonnenuntergangsphasen
- Tibber oder generische Strompreis-Entitaeten
- wetterabhaengige Dimmung und Wolkensimulation
- Simulationsmodus ohne Lichtbefehle
- Zeitraffer-Simulation zum Testen der Tageslogik
- mehrere Aquarien mit eigener Konfiguration
- Dienste mit Aquarium-Auswahl fuer getrennte Lichtsteuerungen
- Dashboard-Export pro Aquarium mit automatisch passenden Entity-IDs
- eigenes Aquarium-LED-Icon und Logo fuer Home Assistant
- aquarium-spezifische Helper-Pakete fuer Blueprint- und Legacy-Setups
- optionaler Legacy-Blueprint, fuer neue Setups nicht mehr erforderlich
- exportierte Dashboard-Karten fuer Cockpit-, Technikpanel- und Simulator-Ansichten
- eine Live-Entitaet pro Aquarium, zum Beispiel `sensor.aquarium_status`

## Installation

1. Fuege dieses Repository in HACS als benutzerdefiniertes Repository mit Kategorie `Integration` hinzu.
2. Installiere `Aquarium LED Cockpit`.
3. Starte Home Assistant neu.
4. Fuege die Integration unter `Einstellungen -> Geraete & Dienste` hinzu.
5. Waehle deine Licht-, Wetter-, Sonnen- und optionalen Preis-Entitaeten aus.

## Enthalten

- Aquarium-Lichtsteuerung direkt in der Integration
- Optionaler Aquarium-Licht-Blueprint als Kompatibilitaetsweg
- Sensorbasierte Markdown-Dashboard-Karte
- Visuelle Cockpit-Dashboard-Karte
- Technikpanel-Dashboard-Karte
- Lovelace-Simulator-Karte mit Horizont und Tageskurve
- Optionaler Legacy-Helfer-Export

Repository: https://github.com/Thomash100/HA-Aquarium-
