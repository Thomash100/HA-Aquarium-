# Aenderungsprotokoll

## V260523.014_BETA.00

Konfigurierbaren Ein- bis Zehn-Minuten-Tageslauf fuer die Simulation umgesetzt.

- Laesst einen kompletten simulierten 24-Stunden-Tag standardmaessig in einer realen Minute durchlaufen.
- Erlaubt ueber die bestehende Zeitraffer-Number eine Gesamtdauer von einer bis zehn Minuten.
- Aktualisiert die Simulation sekundenweise und gleicht Zeitabweichungen ueber eine monotone Laufzeituhr aus.
- Verhindert waehrend des Zeitraffers weiterhin alle Lichtbefehle und vermeidet sekundenweise Schreibzugriffe auf den Speicher.
- Ergaenzt einen direkten Dauerregler in der Simulator-Karte und zeigt Geschwindigkeit sowie Dauer im Status.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.14`.

## V260523.013_BETA.00

Realen Sonnenverlauf und reduziertes Mondlicht umgesetzt.

- Startet den roten Morgenverlauf zum echten Sonnenaufgang aus `sun.sun` und blendet in 60 Minuten zu kuehlem Tagesweiss.
- Beginnt den Abendverlauf 90 Minuten vor dem echten Sonnenuntergang und erreicht dort tiefes Rot.
- Nutzt danach ein stark reduziertes, kuehles Mondlicht mit kleinem Weissanteil und der vorhandenen Nachtlicht-Helligkeit.
- Zeigt die echten Ereigniszeiten und Uebergangsfenster in Statussensor und Dashboard-Kurve.
- Sichert die Phasengrenzen und RGBW-Farben mit automatisierten Tests ab.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.13`.

## V260523.012_BETA.00

Preis- und Batterieverlaeufe in das Dashboard aufgenommen.

- Zeigt 12 Stunden Strompreis-Rueckblick aus der Home-Assistant-Historie.
- Ergaenzt bis zu 24 Stunden echte Viertelstunden-Vorschau ueber `tibber.get_prices`.
- Zeigt 24 Stunden Growatt-/NOAH-Ladezustand mit Vollgrenze, Minimum, Maximum und Aenderung.
- Laedt Verlaufsdaten asynchron und aktualisiert sie alle fuenf Minuten.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.12`.

## V260523.011_BETA.00

Options-Flow fuer Home Assistant 2026.8 kompatibel gemacht.

- Verwendet fuer den Config-Entry eine eigene interne Referenz statt der neuen schreibgeschuetzten Basisklassen-Eigenschaft.
- Stellt damit den Konfigurationsdialog fuer Growatt-Speicher, Solarleistung und Voll-Schwelle wieder her.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.11`.

## V260523.010_BETA.00

Growatt-/NOAH-Speicher und regionale Sonne in die Preissteuerung aufgenommen.

- Ergaenzt konfigurierbare Entitaeten fuer Speicher-Ladezustand und Solarleistung.
- Ignoriert die Strompreis-Dimmung, sobald der Speicher die konfigurierbare Voll-Schwelle erreicht.
- Nutzt standardmaessig 95 Prozent als Voll-Schwelle.
- Zeigt Speicher, Solarleistung, regionalen Sonnenschein und den Status der Preisregel im Cockpit.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.10`.

## V260523.009_BETA.00

Strompreis-Dimmung an das tatsaechliche Tagespreisniveau gekoppelt.

- Dimmt erst oberhalb des Tagesdurchschnitts und danach linear staerker bis zum Tageshoechstpreis.
- Nutzt die eingestellte Preisdimmung als echte maximale Reduktion statt als schwachen Multiplikator auf den absoluten Preis.
- Unterstuetzt Tagesrangfolge und einheitenabhaengige Preisfenster als Fallback fuer generische Preissensoren.
- Zeigt die tatsaechliche Preis-Dimmung direkt in Statussensor und Simulator-Karte.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.9`.

## V260523.008_BETA.00

Nicht mehr benoetigte Ressourcen entfernt.

- Entfernt den alten Automation-Blueprint aus den ausgelieferten Ressourcen.
- Entfernt Legacy-Karten, Helper-Pakete und YAML-Dashboard-Beispiele.
- Behaelt nur die native Integration, Branding und die Lovelace-Simulator-Ressource.
- Vereinfacht den Ressourcenexport auf die Simulator-Frontend-Datei.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.8`.

## V260523.007_BETA.00

Blueprint auf optionalen Kompatibilitaetsweg umgestellt.

- Schaltet den Blueprint-Export fuer neue Setups standardmaessig aus.
- Kennzeichnet den Blueprint in Services und Dokumentation als Legacy-/Expertenoption.
- Ergaenzt im Blueprint eine Aquarium-Konfigurationsauswahl fuer mehrere Aquarien.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.7`.

## V260523.006_BETA.00

Aquarium-spezifische Helper-Pakete fuer mehrere Lichtsteuerungen.

- Exportiert das Helper-Paket pro Aquarium unter eigenem Dateinamen.
- Schreibt Helper-Entity-IDs beim Export auf den Aquarium-Namen um, zum Beispiel `juwel_aquarium_led_simulation_mode`.
- Verhindert, dass mehrere Aquarien globale `input_boolean`- und `input_number`-Helfer teilen.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.6`.

## V260523.005_BETA.00

Lokales Branding fuer die Home-Assistant-Integration.

- Fuegt ein eigenes Aquarium-LED-Icon als `brand/icon.png` hinzu.
- Fuegt ein passendes Logo als `brand/logo.png` hinzu.
- Dokumentiert das lokale Home-Assistant-Branding.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.5`.

## V260523.004_BETA.00

Korrigierter Dashboard-Export fuer mehrere Aquarien.

- Exportiert Dashboard-Snippets pro Aquarium in eigene Unterordner.
- Ersetzt die Standard-Entity-IDs beim Export automatisch passend zum Aquarium-Namen.
- Aktualisiert die Dokumentation fuer erneuten Ressourcenexport und passende Dashboard-Pfade.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.4`.

## V260523.003_BETA.00

Mehr-Aquarium-Dienste fuer getrennte Lichtsteuerungen.

- Stellt die Service-Felder fuer `install_resources` und `set_dashboard_status` auf eine Aquarium-Konfigurationsauswahl um.
- Dokumentiert klar, dass bei mehreren Aquarien der Ziel-Config-Entry gewaehlt werden muss.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.3`.

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
