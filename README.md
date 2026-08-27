# Aquarium LED Cockpit

Aquarium LED Cockpit ist eine Home-Assistant-Custom-Integration fuer eine dynamische Aquarium-Beleuchtung mit strompreisabhaengiger Dimmung, wetterbasierter Wolkensimulation, Sonnenaufgangs-/Sonnenuntergangsphasen und Lovelace-Simulator-Karte.

Veroeffentlichungskennzeichen: `V260816.026_BETA.00`

Home-Assistant-Manifest-Version: `26.8.16-beta.26`

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
- Echter RGBW-Sonnenverlauf aus `sun.sun` mit getrennt einstellbarer Dauer fuer Auf- und Untergang
- Vier frei einstellbare RGBW-Farbpunkte fuer Anfang und Ende von Sonnenaufgang sowie Sonnenuntergang; alle Kanaele werden dazwischen stufenlos linear ueberblendet
- Eigenstaendiges 24-Stunden-Wirkungsdiagramm fuer Grundprofil, effektive Lichtintensitaet, Wolkenfaktor, Preisfaktor und Growatt-Akku-Ladezustand
- Geschwungener Tagesverlauf statt Plateau: Das eingestellte Tagesmaximum wird um 12:00 Uhr erreicht und faellt zu den Uebergangsphasen sanft ab
- Durchgaengiges blaues Mondlicht nach Sonnenuntergang ohne Weisskanal; die eingestellte Nachtlicht-Helligkeit bildet die Vollmond-Obergrenze
- Mondphasenabhaengige Nachthelligkeit mit sanfter Wolkensimulation und mindestens einem Prozent Licht statt Ein/Aus-Schalten
- Sonnenbahn mit echten Auf-/Untergangszeiten und realer Mondphase aus `sensor.moon_phase`
- Einstellbare Lichttag-Verschiebung von minus sechs bis plus sechs Stunden mit grossen 15-Minuten-Tasten und direktem Stundenfeld; Aufgang, Tagesmaximum und Untergang wandern gemeinsam und duerfen ueber Mitternacht laufen, die reale Sonnenbahn bleibt davon unberuehrt
- Deutlich sichtbare Wolkensimulation tagsueber: reale Bewoelkung und eingestellte Wolkenstaerke erzeugen einen staerkeren Grundabschlag und dynamische Wolkenwellen
- Simulationsmodus, der den Cockpit-Status aktualisiert, ohne Lichtbefehle zu senden
- Konfigurierbarer 24-Stunden-Zeitraffer: ein kompletter Tag in einer bis zehn realen Minuten
- Tibber-Unterstuetzung und generische Preis-Entitaeten fuer andere Anbieter
- Adaptive strompreisabhaengige Dimmung: bis zum Tagesdurchschnitt ungedimmt, danach progressiv und deutlich staerker bis zur eingestellten maximalen Dimmung am Tageshoechstpreis
- Growatt-/NOAH-Speicherprioritaet: Ab 90 Prozent SOC wird die Strompreis-Dimmung nur ignoriert, solange die Akku-Ladeleistung groesser als die Entladeleistung ist
- Stufenloser PV-/SOC-Energiefaktor: Bei niedriger PV-Deckung und niedrigem Akku-SOC sinkt das normale Tagesprofil bis auf 30 Prozent; gute PV-Deckung und hoher SOC geben es bis 100 Prozent frei
- Gemeinsame Intensitaetssteuerung fuer beliebig viele Ausgaenge, einschliesslich einer RGBW-Steuerung und zwei separat einstellbaren Weisskanaelen
- Anzeige von Speicher-Ladezustand, Solarleistung und regionalem Sonnenschein im Live-Status
- Strompreis-Diagramm mit 12 Stunden Rueckblick und bis zu 24 Stunden echter Tibber-Vorschau
- Batterie-Diagramm mit 24 Stunden Ladezustands-Rueckblick und konfigurierbarer Vollgrenze
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

> Die native Integration darf nicht gemeinsam mit der alten Blueprint-Automation dieselben Leuchten steuern. Deaktiviere die Blueprint-Automation nach der Migration, damit sich Lichtbefehle und Uebergangszeiten nicht ueberlagern.

## Entitaeten und Dienste

### Live-Entitaeten

| Entitaet | Beschreibung |
| --- | --- |
| `sensor.<aquarium>_status` | Live-Statussensor fuer die exportierten Dashboard-Karten |
| `switch.<aquarium>_steuerung` | Aktiviert die direkte Lichtsteuerung durch die Integration |
| `switch.<aquarium>_simulation` | Berechnet den Status, ohne Lichtbefehle zu senden |
| `switch.<aquarium>_zeitraffer` | Fuehrt eine sichere Zeitraffer-Simulation ohne Lichtbefehle aus |
| `switch.<aquarium>_zeitraffer_am_aquarium` | Spielt nach Bestaetigung genau einen Zeitraffer-Durchlauf auf den echten Leuchten ab und stellt anschliessend deren vorherigen Zustand wieder her |
| `number.<aquarium>_simulationszeit` | Simulierte Minute des Tages, wobei `360` fuer `06:00` steht |
| `number.<aquarium>_sonnenaufgang_verschiebung` | Verschiebt den kompletten Lichttag – Aufgang, Tagesmaximum und Untergang – in Viertelstundenschritten um minus sechs bis plus sechs Stunden; `0` folgt der echten Sonne. Der Entitaetsname stammt aus der Zeit, in der nur der Aufgang verschoben wurde |
| `number.<aquarium>_sonnenaufgang_dauer` | Dauer des farbigen Sonnenaufgangs von 10 bis 240 Minuten |
| `number.<aquarium>_sonnenuntergang_dauer` | Dauer des farbigen Sonnenuntergangs von 10 bis 240 Minuten |
| `number.<aquarium>_zeitraffer_schritt` | Gesamtdauer eines simulierten 24-Stunden-Tages, einstellbar von 1 bis 10 Minuten |
| `number.<aquarium>_weisskanal_1` | Anteil des ersten separaten Weissausgangs am berechneten RGBW-W-Kanal von 0 bis 100 Prozent |
| `number.<aquarium>_weisskanal_2` | Anteil des zweiten separaten Weissausgangs am berechneten RGBW-W-Kanal von 0 bis 100 Prozent |

### Strompreis-Dimmung

Wenn der Preissensor Tagesdurchschnitt und Tageshoechstpreis bereitstellt, bleibt die Beleuchtung bis zum Durchschnitt ungedimmt. Oberhalb des Durchschnitts steigt die Dimmung progressiv an: Schon im mittleren Hochpreisbereich ist der Einfluss deutlich sichtbar, am Tageshoechstpreis erreicht sie weiterhin exakt den Wert von `number.<aquarium>_preisdimmung`. Bei 72 Prozent Preisdimmung bleiben am Tageshoechstpreis somit 28 Prozent der normalen Helligkeit uebrig. Fuer generische Preissensoren nutzt die Integration alternativ die Tagesrangfolge oder ein zur Einheit passendes Preisfenster.

Optional koennen Speicher-Ladezustand, Akku-Ladeleistung, Akku-Entladeleistung, PV-Erzeugung und Leistungsabgabe ausgewaehlt werden. Tagsueber vergleicht ein stufenloser Energiefaktor die aktuelle PV-Erzeugung mit der Leistungsabgabe und kombiniert diese PV-Deckung zu gleichen Teilen mit dem Akku-SOC. Bei fehlender PV-Deckung und einem SOC von 20 Prozent oder weniger wirkt mindestens 30 Prozent des normalen Lichtprofils; bei voller PV-Deckung und 90 Prozent SOC werden 100 Prozent freigegeben. Preis und Wolken wirken weiterhin zusaetzlich. Fehlt einer der drei Messwerte, greift die Integration ausfallsicher nicht in die Helligkeit ein.

Ab der konfigurierten SOC-Schwelle, standardmaessig 90 Prozent, wird die Preis-Dimmung nur dann ignoriert und tagsueber ein Lichtbonus von 15 Prozent angewendet, wenn die aktuelle Ladeleistung strikt groesser als die Entladeleistung ist. Sobald der Speicher gleich stark oder staerker entlaedt, endet die Akku-Prioritaet sofort und die Preisregel greift wieder. Das Ergebnis bleibt zum Schutz des Aquariums auf die eingestellte Tageshelligkeit begrenzt. RGBW-Leuchten erhalten die berechnete Helligkeit und Farbe; alle ausgewaehlten Weiss-Leuchten erhalten gleichzeitig die aus dem W-Kanal abgeleitete Helligkeit. Regionale Sonne wird aus der ausgewaehlten Wetter-Entitaet erkannt und zusammen mit den realen Leistungswerten im Statussensor dargestellt.

Die Simulator-Karte laedt die letzten 12 Stunden Strompreis und 24 Stunden Batterie-Ladezustand direkt aus der Home-Assistant-Historie. Wenn die Tibber-Aktion `tibber.get_prices` verfuegbar ist, ergaenzt sie die Preislinie um die bereits veroeffentlichten Viertelstundenpreise der naechsten 24 Stunden. Das separate Wirkungsdiagramm berechnet daraus die effektive Tageshelligkeit inklusive staerkerer Preisregel, sichtbarer Wolkenwellen, Akku-SOC, PV-/SOC-Energiefaktor und der aktuellen Lade-/Entladebilanz. Das Grundprofil erreicht sein Sollmaximum um 12:00 Uhr; die Ergebnislinie kann durch Preis, Wolken und knappe Solarenergie darunter liegen. Fuer die Zukunft werden der letzte echte Akku-Ladezustand sowie aktuelle PV-Erzeugung, Leistungsabgabe und Ladebilanz gehalten und als solche gekennzeichnet; eine kuenstliche Akku- oder PV-Prognose wird nicht erzeugt.

### Sonnenaufgang und Mondlicht

Das Mondlicht beginnt am Licht-Sonnenuntergang und bleibt bis zum Licht-Sonnenaufgang aktiv. Mit `number.<aquarium>_sonnenaufgang_verschiebung` laesst sich der gesamte Lichttag relativ zur echten Sonne verschieben: `+2` startet den roten Lichtaufgang zwei Stunden spaeter und beendet den Untergang ebenfalls zwei Stunden spaeter; `-1` zieht beide Enden eine Stunde vor. Die Laenge des Lichttages und damit die Nachtdauer bleiben unveraendert, und das Tagesmaximum wandert mit. Die reale Sonnen- und Mondbahn bleiben fest. Der Lichttag darf dabei ueber Mitternacht laufen: bei Sonnenaufgang 06:12 und -untergang 20:05 ergibt `+6` einen Lichttag von 12:12 bis 02:05 des Folgetages. Die Phasenlogik rechnet dafuer nicht in Uhrzeiten, sondern in Minuten seit dem Lichtaufgang. In der Cockpit-Karte erfolgt die Einstellung mobil bedienbar ueber grosse Minus-/Plus-Tasten in 15-Minuten-Schritten oder direkt ueber das Stundenfeld. Die Dauer-Felder mit grossen Minus-/Plus-Tasten legen getrennt fest, wie lange Auf- und Untergang dauern. Fuer Anfang und Ende jedes Uebergangs lassen sich Rot, Gruen, Blau und Weiss mit grossen Reglern von 0 bis 255 einstellen. Die Integration interpoliert jeden Kanal stufenlos. Die Sonnenbahn bleibt dabei eine reine Himmelsdarstellung; die wirksame Intensitaet steht in einem eigenen Diagramm darunter.

Die beiden separaten Weiss-Leuchten besitzen eigene Regler von 0 bis 100 Prozent. Diese Werte skalieren den jeweils berechneten RGBW-Weissanteil: 100 Prozent folgt dem W-Kanal vollstaendig, 50 Prozent gibt die Haelfte davon aus und 0 Prozent schaltet nur den betreffenden Weissausgang ab. RGB und der jeweils andere Weisskanal bleiben davon unberuehrt.

### Zeitraffer-Simulation

Aktiviere den Zeitraffer-Schalter, um einen ganzen Tag zu testen, ohne echte Lichter zu veraendern. Die Integration nutzt die Simulationszeit als Uhr und schreibt Phase, Helligkeit sowie RGBW-Zielwerte sekundenweise in den Statussensor. Der komplette 24-Stunden-Tag wird in der eingestellten Gesamtdauer von 1 bis 10 Minuten durchlaufen und anschliessend fortlaufend wiederholt, bis der Zeitraffer gestoppt wird.

Mit `Zeitraffer am Aquarium` kann derselbe Verlauf bewusst einmalig auf den konfigurierten echten Leuchten betrachtet werden. Die normale Steuerung muss dafuer eingeschaltet sein. Vor dem Start sichert die Integration Ein/Aus-Zustand, Helligkeit und Farbe jeder erreichbaren Leuchte. Nach einem vollstaendigen Durchlauf oder beim manuellen Stopp wird dieser Zustand automatisch wiederhergestellt. Die physischen Vorschau-Uebergaenge sind auf maximal eine Sekunde begrenzt, damit der beschleunigte Verlauf sichtbar bleibt.

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

#### `aquarium_led_cockpit.set_transition_color`

Speichert einen RGBW-Farbpunkt am Anfang oder Ende eines Sonnenaufgangs beziehungsweise Sonnenuntergangs. Die Simulator-Karte ruft diesen Dienst ueber ihre vier RGBW-Reglergruppen auf.

| Feld | Erforderlich | Beschreibung |
| --- | --- | --- |
| `config_entry_id` | Nein | Aquarium-Konfiguration; bei mehreren Eintraegen erforderlich |
| `phase` | Ja | `sunrise_start`, `sunrise_end`, `sunset_start` oder `sunset_end`; `sunrise` und `sunset` bleiben als kompatible Kurzformen erhalten |
| `rgbw_color` | Ja | Vier Werte von 0 bis 255 in der Reihenfolge Rot, Gruen, Blau, Weiss |

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
