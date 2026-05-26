# Aquarium LED Cockpit

Aquarium LED Cockpit ist eine Home-Assistant-Custom-Integration fuer eine dynamische Aquarium-Beleuchtung mit strompreisabhaengiger Dimmung, wetterbasierter Wolkensimulation, Sonnenaufgangs-/Sonnenuntergangsphasen und Lovelace-Simulator-Karte.

Veroeffentlichungskennzeichen: `V260523.008_BETA.00`

Home-Assistant-Manifest-Version: `26.5.23-beta.8`

[![Home Assistant oeffnen und dieses Repository in HACS anzeigen.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Thomash100&repository=HA-Aquarium-&category=integration)
![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)
![GitHub-Veroeffentlichung](https://img.shields.io/github/v/release/Thomash100/HA-Aquarium-?sort=semver)
![Lizenz](https://img.shields.io/github/license/Thomash100/HA-Aquarium-)

Die Integration verwandelt deine Aquarium-Beleuchtung in einen dynamischen Tagesverlauf, der auf Sonne, Strompreise und Wetter reagieren kann. Sie kann direkt in Home Assistant konfiguriert werden, unterstuetzt mehrere Aquarien als getrennte Eintraege, stellt eigene Steuer-Entitaeten fuer den Alltag bereit und liefert je Aquarium einen eigenen Live-Statussensor.

> Demo-Medien und Screenshots koennen spaeter ergaenzt werden. Die Repository-Struktur ist bereits fuer eine HACS-Praesentation vorbereitet.

## Inhaltsverzeichnis

- [Funktionen](#funktionen)
- [Installation](#installation)
- [Schnellstart](#schnellstart)
- [Dashboard-Varianten](#dashboard-varianten)
- [Entitaeten und Dienste](#entitaeten-und-dienste)
- [Veroeffentlichungshistorie](#veroeffentlichungshistorie)
- [Versionierung](#versionierung)
- [Exportierte Dateien](#exportierte-dateien)
- [Fehlerbehebung](#fehlerbehebung)
- [Repository-Struktur](#repository-struktur)
- [Lizenz](#lizenz)

## Funktionen

- Dynamische Aquarium-LED-Steuerung fuer Shelly-RGBW-Lichter
- Einrichtung per Home-Assistant-Oberflaeche fuer RGBW-Lichter, optionale Weisskanaele, Wetter, Sonne, Preis-Entitaet und Uebergangszeit
- Eigene Switch- und Number-Entitaeten fuer Normalbetrieb, sichere Simulation und Zeitraffer-Test
- Mehrere Aquarien mit eigenem Namen, eigener Runtime und eigenen Entitaeten
- Dienste mit Aquarium-Auswahl, damit Status und Ressourcen gezielt einem Aquarium zugeordnet werden
- Sonnenaufgangs- und Sonnenuntergangsphasen auf Basis von `sun.sun`
- Wolkensimulation tagsueber mit wetterabhaengiger Dimmung
- Simulationsmodus, der den Cockpit-Status aktualisiert, ohne Lichtbefehle zu senden
- Tibber-Unterstuetzung und generische Preis-Entitaeten fuer andere Anbieter
- Strompreisabhaengige Dimmung mit Begrenzung auf guenstige Preisbereiche
- Live-Dashboard-Entitaet pro Aquarium, zum Beispiel `sensor.aquarium_status`
- Eigenes lokales Home-Assistant-Branding mit Aquarium-LED-Icon und Logo
- Lovelace-Simulator-Karte als einzige exportierte Frontend-Ressource

## Installation

### HACS

1. Fuege dieses Repository in HACS als benutzerdefiniertes Repository mit Kategorie `Integration` hinzu.
2. Installiere `Aquarium LED Cockpit`.
3. Starte Home Assistant neu.
4. Oeffne `Einstellungen -> Geraete & Dienste`.
5. Fuege die Integration `Aquarium LED Cockpit` hinzu.

### Home-Assistant-My-Link

Direkter HACS-Link:

[In HACS oeffnen](https://my.home-assistant.io/redirect/hacs_repository/?owner=Thomash100&repository=HA-Aquarium-&category=integration)

## Schnellstart

1. Installiere die Integration ueber HACS.
2. Starte Home Assistant neu.
3. Fuege die Integration unter `Einstellungen -> Geraete & Dienste` hinzu.
4. Gib einen Aquarium-Namen an und waehle RGBW-Lichter sowie optionale Entitaeten im Einrichtungsformular aus.
5. Nutze die erzeugten Switches, Simulationsschalter und Number-Entitaeten in Home Assistant.
6. Lasse `auto_install` aktiviert, wenn die Lovelace-Simulator-Ressource automatisch exportiert werden soll.
7. Fuege bei Bedarf die Simulator-Karte zu Lovelace hinzu.

Nach der Einrichtung kann die Integration exportieren:

- die Lovelace-Simulator-Karte nach `/config/www/aquarium_led_cockpit/aquarium-led-simulator-card.js`

## Dashboard-Varianten

Die alten YAML-Dashboard-Snippets und der Blueprint wurden entfernt, weil die native Integration die Steuerung und Statusdaten selbst bereitstellt. Fuer Lovelace bleibt die Simulator-Karte als echte Frontend-Ressource erhalten:

| Variante | Datei | Zweck |
| --- | --- | --- |
| Simulator-Karte | `aquarium-led-simulator-card.js` | Lovelace-Custom-Card mit Horizont, Tageskurve, Zielhelligkeit und Teststeuerung |

Fuer die Simulator-Karte muss die Lovelace-Ressource `/local/aquarium_led_cockpit/aquarium-led-simulator-card.js` hinzugefuegt werden.

## Entitaeten und Dienste

### Live-Entitaeten

| Entitaet | Beschreibung |
| --- | --- |
| `sensor.<aquarium>_status` | Live-Statussensor fuer die exportierten Dashboard-Karten |
| `switch.<aquarium>_steuerung` | Aktiviert die direkte Lichtsteuerung durch die Integration |
| `switch.<aquarium>_simulation` | Berechnet den Status, ohne Lichtbefehle zu senden |
| `switch.<aquarium>_zeitraffer` | Fuehrt eine sichere Zeitraffer-Simulation ohne Lichtbefehle aus |
| `number.<aquarium>_simulationszeit` | Simulierte Minute des Tages, wobei `360` fuer `06:00` steht |
| `number.<aquarium>_zeitraffer_schritt` | Minuten, die pro echtem Minuten-Takt zur Simulationszeit addiert werden |

### Zeitraffer-Simulation

Aktiviere den Zeitraffer-Schalter, um einen ganzen Tag zu testen, ohne echte Lichter zu veraendern. Die Integration nutzt die Simulationszeit als Uhr, schreibt Phase, Helligkeit und RGBW-Zielwerte in den Statussensor des jeweiligen Aquariums und verschiebt die simulierte Zeit einmal pro echter Minute um den eingestellten Zeitraffer-Schritt.

## Veroeffentlichungshistorie

Veroeffentlichungen werden aus Versions-Tags erstellt und in `CHANGELOG.md` dokumentiert, damit HACS auswaehlbare Versionen mit Versionshinweisen anzeigen kann.

## Versionierung

Sichtbare Veroeffentlichungskennzeichen verwenden waehrend der Beta-Phase `VYYMMDD.NNN_BETA.xx`. `YYMMDD` ist das Erscheinungsdatum bei grundlegenden Aenderungen, `NNN` ist der Anpassungsindex fuer kompatible Folgeaenderungen innerhalb dieser Veroeffentlichungslinie und `xx` ist die Beta-Iteration. Sobald eine Veroeffentlichungslinie stabil ist, wird der `_BETA.xx`-Suffix entfernt. Home Assistant erhaelt parallel eine kompatible Manifest-Version wie `26.5.23-beta.8`.

### Dienste

#### `aquarium_led_cockpit.install_resources`

Kopiert die Lovelace-Simulator-Ressource in die Home-Assistant-Konfiguration.

| Feld | Erforderlich | Beschreibung |
| --- | --- | --- |
| `config_entry_id` | Nein | Aquarium-Konfiguration, deren Exportoptionen genutzt werden sollen. Bei mehreren Eintraegen gezielt auswaehlen |
| `export_frontend_resources` | Nein | Lovelace-Simulator-Karte nach `/config/www/aquarium_led_cockpit/` exportieren |
| `overwrite_existing` | Nein | Bereits vorhandene Dateien ersetzen |

#### `aquarium_led_cockpit.set_dashboard_status`

Aktualisiert den Live-Statussensor aus einer Automation oder einem Skript.

| Feld | Erforderlich | Beschreibung |
| --- | --- | --- |
| `config_entry_id` | Nein | Aquarium-Konfiguration, deren Live-Status aktualisiert werden soll. Bei mehreren Eintraegen erforderlich |
| `status_json` | Ja | Kompaktes JSON-Objekt mit dem Aquarium-Lichtstatus |

Wenn mehrere Aquarien eingerichtet sind, trennt die Integration Runtime, Speicher, Sensoren, Schalter, Zahlen und Dienstaufrufe pro Config-Entry. Dadurch koennen unterschiedliche Aquarium-Lichtsteuerungen parallel laufen, ohne sich gegenseitig Status oder Simulation zu ueberschreiben.

## Exportierte Dateien

| Datei | Ziel |
| --- | --- |
| `aquarium-led-simulator-card.js` | `/config/www/aquarium_led_cockpit/` |
| `brand/icon.png`, `brand/logo.png` | lokales Home-Assistant-Branding der Integration |

## Fehlerbehebung

### Die Integration erscheint nach der HACS-Installation nicht

- Starte Home Assistant nach der HACS-Installation neu.
- Pruefe, ob die Repository-Kategorie in HACS `Integration` ist.
- Pruefe, ob `custom_components/aquarium_led_cockpit/` in deiner Home-Assistant-Konfiguration vorhanden ist.

### Der Config Flow schlaegt beim Einrichten fehl

- Entferne die Integration und installiere sie ueber HACS erneut.
- Starte Home Assistant vollstaendig neu und versuche es danach erneut.
- Pruefe `Einstellungen -> System -> Protokolle` auf den Fehler.

### Simulator-Karte zeigt keine Daten

- Pruefe, ob der Statussensor des Aquariums existiert, zum Beispiel `sensor.aquarium_status`.
- Exportiere die Ressourcen nach dem Update erneut und aktiviere bei Bedarf `Vorhandene Dateien ueberschreiben`.
- Stelle fuer die Simulator-Karte sicher, dass `/local/aquarium_led_cockpit/aquarium-led-simulator-card.js` als Lovelace-Ressource eingetragen ist.

### Lovelace-Ressource wurde nicht exportiert

Fuehre den Export-Dienst manuell aus:

```yaml
service: aquarium_led_cockpit.install_resources
data:
  export_frontend_resources: true
  overwrite_existing: false
```

## Repository-Struktur

- `custom_components/aquarium_led_cockpit/` enthaelt den Integrationscode.
- `custom_components/aquarium_led_cockpit/resources/` enthaelt die Lovelace-Simulator-Ressource.
- `.github/workflows/` enthaelt HACS-, Hassfest- und Veroeffentlichungsablaeufe.
- `info.md` ist die kurze Beschreibung fuer HACS.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE).
<!-- SYSTEMMEDIA_LEGAL_START -->
## Rechtliche Hinweise

- Impressum: https://systemmedia.de/impressum/
- Datenschutz / DSGVO-Hinweise: https://systemmedia.de/datenschutz/
- Nutzungsbedingungen und Haftungsausschluss: https://systemmedia.de/nutzungsbedingungen/

Dieses Repository enthaelt, sofern nicht ausdruecklich anders gekennzeichnet, Test-, Entwicklungs-, Demonstrations- oder Evaluierungsinhalte. Nutzung auf eigene Verantwortung.

Soweit eine `LICENSE`-Datei vorhanden ist, gelten die dort genannten Lizenzbedingungen fuer die eingeraeumten Nutzungsrechte. Ergaenzend gelten die Status-, Gewaehrleistungs- und Haftungshinweise in `LEGAL.md`.
<!-- SYSTEMMEDIA_LEGAL_END -->
