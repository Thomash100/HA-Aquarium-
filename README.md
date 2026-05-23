# Aquarium LED Cockpit

Aquarium LED Cockpit ist eine Home-Assistant-Custom-Integration fuer eine dynamische Aquarium-Beleuchtung mit strompreisabhaengiger Dimmung, wetterbasierter Wolkensimulation, Sonnenaufgangs-/Sonnenuntergangsphasen und vorbereiteten Dashboard-Ansichten.

Veroeffentlichungskennzeichen: `V260523.001_BETA.00`

Home-Assistant-Manifest-Version: `26.5.23-beta.1`

[![Home Assistant oeffnen und dieses Repository in HACS anzeigen.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Thomash100&repository=HA-Aquarium-&category=integration)
![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)
![GitHub-Veroeffentlichung](https://img.shields.io/github/v/release/Thomash100/HA-Aquarium-?sort=semver)
![Lizenz](https://img.shields.io/github/license/Thomash100/HA-Aquarium-)

Die Integration verwandelt deine Aquarium-Beleuchtung in einen dynamischen Tagesverlauf, der auf Sonne, Strompreise und Wetter reagieren kann. Sie kann direkt in Home Assistant konfiguriert werden, stellt eigene Steuer-Entitaeten fuer den Alltag bereit, bringt den Blueprint als Kompatibilitaetsweg mit, exportiert Dashboard-Karten und liefert einen Live-Statussensor fuer Cockpit-Ansichten.

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
- Sonnenaufgangs- und Sonnenuntergangsphasen auf Basis von `sun.sun`
- Wolkensimulation tagsueber mit wetterabhaengiger Dimmung
- Simulationsmodus, der den Cockpit-Status aktualisiert, ohne Lichtbefehle zu senden
- Tibber-Unterstuetzung und generische Preis-Entitaeten fuer andere Anbieter
- Strompreisabhaengige Dimmung mit Begrenzung auf guenstige Preisbereiche
- Optionaler Legacy-`input_text`-Export fuer aeltere Dashboard-Setups
- Live-Dashboard-Entitaet: `sensor.aquarium_led_cockpit_status`
- Visuelle Dashboard-Karten fuer Cockpit- und Technikpanel-Ansichten
- Ein-Klick-Export von Blueprint- und Dashboard-Dateien fuer Legacy- oder manuelle Workflows

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
4. Waehle RGBW-Lichter und optionale Entitaeten im Einrichtungsformular aus.
5. Nutze die erzeugten Switches, Simulationsschalter und Number-Entitaeten in Home Assistant.
6. Lasse `auto_install` aktiviert, wenn Blueprint und Dashboard-Snippets zusaetzlich exportiert werden sollen.
7. Fuege bei Bedarf eine der exportierten Dashboard-Karten zu Lovelace hinzu.

Nach der Einrichtung kann die Integration exportieren:

- den Aquarium-Blueprint nach `/config/blueprints/automation/aquarium_led_cockpit/`
- sensorbasierte Dashboard-Karten nach `/config/aquarium_led_cockpit/dashboard/`
- Dashboard-Steuerhelfer nach `/config/packages/aquarium_led_cockpit_controls.yaml`
- optionale Legacy-Helfer und Legacy-Karten fuer aeltere Setups

Das Helper-Paket benoetigt aktivierte Home-Assistant-Packages, zum Beispiel
`homeassistant: packages: !include_dir_named packages` in `configuration.yaml`.

## Dashboard-Varianten

Die Integration liefert derzeit fuenf Dashboard-Snippets:

| Variante | Datei | Zweck |
| --- | --- | --- |
| Markdown-Status | `aquarium_led_status_sensor.yaml` | Schlanke Statusuebersicht ohne Custom Cards |
| Visuelles Cockpit | `aquarium_led_cockpit_visual_button_card_sensor.yaml` | Einzelkarte mit RGBW-, Preis-, Wetter- und Phasenstatus |
| Technikpanel | `aquarium_led_technikpanel_sensor.yaml` | Mehrteilige Technikansicht mit Licht-, Preis-, Wetter- und Zeitbereichen |
| Steuerpanel | `aquarium_led_controls_panel.yaml` | Entitaetssteuerung fuer Helligkeit, Wolkenstaerke, Wartung, Simulation und manuelles RGBW |
| 24h-Status | `aquarium_led_power_price_24h.yaml` | 24h-Verlaufskarte mit dem eingebauten Cockpit-Statussensor, bereit fuer optionale Leistungs- und Preissensoren |

Fuer die visuellen Varianten wird `custom:button-card` ueber HACS benoetigt.

## Entitaeten und Dienste

### Live-Entitaeten

| Entitaet | Beschreibung |
| --- | --- |
| `sensor.aquarium_led_cockpit_status` | Live-Statussensor fuer die exportierten Dashboard-Karten |
| `switch.aquarium_led_steuerung` | Aktiviert die direkte Lichtsteuerung durch die Integration |
| `switch.aquarium_led_simulation` | Berechnet den Status, ohne Lichtbefehle zu senden |
| `switch.aquarium_led_zeitraffer` | Fuehrt eine sichere Zeitraffer-Simulation ohne Lichtbefehle aus |
| `number.aquarium_led_simulationszeit` | Simulierte Minute des Tages, wobei `360` fuer `06:00` steht |
| `number.aquarium_led_zeitraffer_schritt` | Minuten, die pro echtem Minuten-Takt zur Simulationszeit addiert werden |

### Zeitraffer-Simulation

Aktiviere den Zeitraffer-Schalter, um einen ganzen Tag zu testen, ohne echte Lichter zu veraendern. Die Integration nutzt die Simulationszeit als Uhr, schreibt Phase, Helligkeit und RGBW-Zielwerte nach `sensor.aquarium_led_cockpit_status` und verschiebt die simulierte Zeit einmal pro echter Minute um den eingestellten Zeitraffer-Schritt.

## Veroeffentlichungshistorie

Veroeffentlichungen werden aus Versions-Tags erstellt und in `CHANGELOG.md` dokumentiert, damit HACS auswaehlbare Versionen mit Versionshinweisen anzeigen kann.

## Versionierung

Sichtbare Veroeffentlichungskennzeichen verwenden waehrend der Beta-Phase `VYYMMDD.NNN_BETA.xx`. `YYMMDD` ist das Erscheinungsdatum bei grundlegenden Aenderungen, `NNN` ist der Anpassungsindex fuer kompatible Folgeaenderungen innerhalb dieser Veroeffentlichungslinie und `xx` ist die Beta-Iteration. Sobald eine Veroeffentlichungslinie stabil ist, wird der `_BETA.xx`-Suffix entfernt. Home Assistant erhaelt parallel eine kompatible Manifest-Version wie `26.5.23-beta.1`.

### Dienste

#### `aquarium_led_cockpit.install_resources`

Kopiert die mitgelieferten Blueprint- und Dashboard-Ressourcen in die Home-Assistant-Konfiguration.

| Feld | Erforderlich | Beschreibung |
| --- | --- | --- |
| `config_entry_id` | Nein | Optionale Config-Entry-ID, falls mehrere Eintraege existieren |
| `install_blueprint` | Nein | Aquarium-Blueprint exportieren |
| `export_dashboard_snippets` | Nein | Sensorbasierte Dashboard-Snippets exportieren |
| `export_legacy_files` | Nein | Legacy-Helfer und Legacy-Karten exportieren |
| `overwrite_existing` | Nein | Bereits vorhandene Dateien ersetzen |

#### `aquarium_led_cockpit.set_dashboard_status`

Aktualisiert den Live-Statussensor aus einer Automation oder einem Skript.

| Feld | Erforderlich | Beschreibung |
| --- | --- | --- |
| `status_json` | Ja | Kompaktes JSON-Objekt mit dem Aquarium-Lichtstatus |

## Exportierte Dateien

| Datei | Ziel |
| --- | --- |
| `aquarium_led_tibber_weather_shelly_rgbw.yaml` | `/config/blueprints/automation/aquarium_led_cockpit/` |
| `aquarium_led_status_sensor.yaml` | `/config/aquarium_led_cockpit/dashboard/` |
| `aquarium_led_cockpit_visual_button_card_sensor.yaml` | `/config/aquarium_led_cockpit/dashboard/` |
| `aquarium_led_technikpanel_sensor.yaml` | `/config/aquarium_led_cockpit/dashboard/` |
| `aquarium_led_controls_panel.yaml` | `/config/aquarium_led_cockpit/dashboard/` |
| `aquarium_led_power_price_24h.yaml` | `/config/aquarium_led_cockpit/dashboard/` |
| `aquarium_led_cockpit_controls.yaml` | `/config/packages/` |
| `aquarium_led_dashboard_status_helper.yaml` | optionaler Legacy-Export nach `/config/packages/` |

## Fehlerbehebung

### Die Integration erscheint nach der HACS-Installation nicht

- Starte Home Assistant nach der HACS-Installation neu.
- Pruefe, ob die Repository-Kategorie in HACS `Integration` ist.
- Pruefe, ob `custom_components/aquarium_led_cockpit/` in deiner Home-Assistant-Konfiguration vorhanden ist.

### Der Config Flow schlaegt beim Einrichten fehl

- Entferne die Integration und installiere sie ueber HACS erneut.
- Starte Home Assistant vollstaendig neu und versuche es danach erneut.
- Pruefe `Einstellungen -> System -> Protokolle` auf den Fehler.

### Dashboard-Karten zeigen keine Daten

- Pruefe, ob `sensor.aquarium_led_cockpit_status` existiert.
- Nutze den exportierten Blueprint oder rufe `aquarium_led_cockpit.set_dashboard_status` auf.
- Stelle fuer visuelle Karten sicher, dass `custom:button-card` installiert ist.

### Blueprint- oder Dashboard-Dateien wurden nicht exportiert

Fuehre den Export-Dienst manuell aus:

```yaml
service: aquarium_led_cockpit.install_resources
data:
  install_blueprint: true
  export_dashboard_snippets: true
  export_legacy_files: false
  overwrite_existing: false
```

## Repository-Struktur

- `custom_components/aquarium_led_cockpit/` enthaelt den Integrationscode.
- `custom_components/aquarium_led_cockpit/resources/` enthaelt Blueprint- und Dashboard-Dateien.
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
