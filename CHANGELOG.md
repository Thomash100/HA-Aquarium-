# Aenderungsprotokoll

## V260523.002_BETA.00

Lovelace-Simulator-Karte und einfache Mehr-Aquarium-Konfiguration.

- Erlaubt mehrere Aquarium-LED-Cockpit-Konfigurationen mit eigenem Aquarium-Namen.
- Trennt Runtime, Statussensor, Schalter und Zahlen je Aquarium.
- Fuegt eine eigene Lovelace-Simulator-Karte mit Horizont, Tageskurve, Zielhelligkeit und Teststeuerung hinzu.
- Exportiert die Simulator-Karte nach `/config/www/aquarium_led_cockpit/` und ein Beispiel-Snippet nach `/config/aquarium_led_cockpit/dashboard/`.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.2`.

## V260523.001_BETA.00

Deutschsprachige Texte fuer Projekt, HACS und Home Assistant.

- Stellt README, HACS-Info und Aenderungsprotokoll auf Deutsch um.
- Stellt Service-Beschreibungen, Integrationsmeldungen und exportierte Hinweise auf Deutsch um.
- Stellt den Versionshinweis-Generator und den GitHub-Veroeffentlichungsablauf auf deutsche Ausgaben um.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.1`.

## V260523.000_BETA.00

Grundlegende Veroeffentlichungslinie fuer die UI-gesteuerte Lichtsteuerung.

- Fuehrt das sichtbare Veroeffentlichungskennzeichen-Schema `VYYMMDD.NNN_BETA.xx` ein.
- Verschiebt das Erscheinungsdatum, weil die UI-gesteuerte Steuerung eine grundlegende Aenderung ist.
- Behaelt die Home-Assistant-Kompatibilitaet ueber Manifest-Version `26.5.23-beta.0` bei.
- Enthaelt UI-gesteuerte Lichtsteuerung, Zeitraffer-Simulation und automatische GitHub-Versionshinweise.

## V260519.003_BETA.00

Veroeffentlichungsverwaltung fuer HACS-Update-Dialoge.

- Fuegt einen automatischen GitHub-Veroeffentlichungsablauf fuer Versions-Tags hinzu.
- Erzeugt Versionshinweise aus diesem Aenderungsprotokoll.
- Trennt die semver-kompatible Home-Assistant-Manifest-Version vom sichtbaren Veroeffentlichungskennzeichen.

## V260519.002_BETA.00

UI-gesteuerte Aquarium-Lichtsteuerung in Anlehnung an Adaptive Lighting.

- Fuegt Einrichtungsoptionen fuer RGBW-Lichter, optionale Weisskanaele, Wetter, Sonne, Preis-Entitaet und Uebergangszeit hinzu.
- Fuegt Switch-Entitaeten fuer Steuerung, Simulation und Zeitraffer hinzu.
- Fuegt Number-Entitaeten fuer Helligkeit, Preisdimmung, Wolkenstaerke, Simulationszeit und Zeitraffer-Geschwindigkeit hinzu.
- Fuegt eine interne Python-Berechnungsengine fuer Phase, Helligkeit, RGBW, Wetter, Wolken und Preisfaktoren hinzu.

## V260519.001_BETA.00

Grundlage fuer Blueprint und Dashboard.

- Fuegt das Grundgeruest der HACS-Custom-Integration hinzu.
- Fuegt den Live-Cockpit-Statussensor hinzu.
- Exportiert Blueprint, Helper-Paket und Dashboard-Snippets.
- Korrigiert die Home-Assistant-Manifest-Version.
