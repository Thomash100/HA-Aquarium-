# Aquarium LED Cockpit

Aquarium LED Cockpit ist eine ueber HACS installierbare Home-Assistant-Custom-Integration fuer dynamische Aquarium-Beleuchtung.

Veroeffentlichungskennzeichen: `V260816.025_BETA.00`

Home-Assistant-Manifest-Version: `26.8.16-beta.25`

Die Integration kombiniert:

- sonnenbasierte Sonnenaufgangs- und Sonnenuntergangsphasen
- Tibber oder generische Strompreis-Entitaeten
- wetterabhaengige Dimmung und Wolkensimulation
- Simulationsmodus ohne Lichtbefehle
- Zeitraffer-Simulation zum Testen der Tageslogik
- mehrere Aquarien mit eigener Konfiguration
- Dienste mit Aquarium-Auswahl fuer getrennte Lichtsteuerungen
- eigenes Aquarium-LED-Icon und Logo fuer Home Assistant
- Lovelace-Simulator-Karte mit getrennter Sonnenbahn und wirksamer Tageskurve
- vier grosse RGBW-Reglergruppen fuer Anfang und Ende von Sonnenaufgang und Sonnenuntergang
- Wirkungsdarstellung fuer Wolken, Strompreis und Growatt-Akku mit Lade-/Entladebilanz
- stufenloser PV-/SOC-Energiefaktor von 30 bis 100 Prozent anhand PV-Erzeugung, Leistungsabgabe und Akku-Ladung
- gemeinsame Ausgabe auf einer RGBW-Steuerung und zwei separaten Weisskanaelen
- geschwungener Tagesverlauf mit Maximum um 12:00 Uhr und verstaerkten Preis- und Wolkeneinflussen
- eine Live-Entitaet pro Aquarium, zum Beispiel `sensor.aquarium_status`

## Installation

1. Fuege dieses Repository in HACS als benutzerdefiniertes Repository mit Kategorie `Integration` hinzu.
2. Installiere `Aquarium LED Cockpit`.
3. Starte Home Assistant neu.
4. Fuege die Integration unter `Einstellungen -> Geraete & Dienste` hinzu.
5. Waehle deine Licht-, Wetter-, Sonnen- und optionalen Preis-Entitaeten aus.

## Enthalten

- Aquarium-Lichtsteuerung direkt in der Integration
- Lovelace-Simulator-Karte mit Sonnenbahn, Intensitaetsverlauf und RGBW-Uebergangssteuerung
- Lokales Home-Assistant-Branding

Repository: https://github.com/Thomash100/HA-Aquarium-
