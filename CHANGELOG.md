# Aenderungsprotokoll

## V260816.019_BETA.00

Einstellbare Verschiebung des Sonnenaufgangs ergaenzt.

- Fuegt je Aquarium den Regler `Sonnenaufgang-Verschiebung` von minus sechs bis plus sechs Stunden in Viertelstundenschritten hinzu.
- Verwendet den verschobenen Lichtstart auch als Ende des durchgaengigen Mondlichts.
- Zeigt echte Sonnenaufgangszeit, verschobenen Lichtstart und eingestellten Versatz gemeinsam im Simulator an.
- Begrenzt extreme negative Verschiebungen auf 00:00 Uhr und extreme positive Verschiebungen auf 23:59 Uhr, ohne den Tageswechsel unbeabsichtigt zu ueberspringen.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.8.16-beta.19`.

## V260523.018_BETA.00

Dauerhaftes, mondphasen- und wolkenabhaengiges Mondlicht ergaenzt.

- Haelt das RGBW-Mondlicht waehrend der gesamten Nacht mit mindestens einem Prozent eingeschaltet.
- Verwendet die eingestellte Nachtlicht-Helligkeit als Vollmond-Obergrenze und reduziert sie fuer Sichel-, Viertel- und Neumondphasen.
- Dimmt das Mondlicht zusaetzlich sanft anhand der realen Bewoelkung und der eingestellten Wolkenstaerke.
- Zeigt effektives Mondlicht, Mondphasenfaktor und Wolkenabschlag in der Simulator-Karte.
- Dokumentiert den Steuerungskonflikt, wenn die alte Blueprint-Automation parallel zur nativen Integration aktiv bleibt.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.18`.

## V260523.017_BETA.00

Sonnen-/Mondbahn und einstellbare RGBW-Uebergangsfarben ergaenzt.

- Ersetzt das bisherige Tagesband durch eine echte Sonnenbahn anhand der Auf- und Untergangszeiten.
- Zeigt nachts eine eigene Mondbahn mit der realen Home-Assistant-Mondphase an.
- Ergaenzt getrennte RGB-Farbwaehler und W-Kanal-Regler fuer Sonnenaufgang und Sonnenuntergang.
- Speichert beide RGBW-Endfarben dauerhaft pro Aquarium und nutzt sie sofort in Livebetrieb und Simulation.
- Ersetzt die missverstaendliche Preisregel-Anzeige `Ignoriert` durch `Pause: Nacht` oder `Pause: Speicher voll`.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.17`.

## V260523.016_BETA.00

RGBW-Farbprofil fuer Sonne und Mond ueberarbeitet.

- Fuehrt Sonnenaufgang und Sonnenuntergang ueber definierte RGBW-Farbstufen: Tiefrot, Orange, Gold, Warmweiss und Tagesweiss.
- Verwendet fuer den Abend exakt die umgekehrte Farbfolge des Morgens.
- Setzt das Mondlicht auf reines, gedimmtes Blau ohne Weissanteil, sodass zusaetzliche Weisskanaele nachts ausgeschaltet bleiben.
- Zeigt die vier aktiven RGBW-Kanalwerte direkt im Dashboard an.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.16`.

## V260523.015_BETA.00

Einmalige Zeitraffer-Vorschau auf den echten Aquarium-Leuchten ergaenzt.

- Fuegt einen getrennten Schalter `Zeitraffer am Aquarium` fuer die bewusste physische Vorschau hinzu.
- Startet jeden physischen Test bei Mitternacht und beendet ihn automatisch nach genau einem simulierten Tag.
- Sichert vor dem Start Ein/Aus-Zustand, Helligkeit und Farbe aller konfigurierten Leuchten.
- Stellt den vorherigen Lichtzustand nach Ablauf, manuellem Stopp oder geordnetem Entladen der Integration wieder her.
- Begrenzt Uebergaenge im beschleunigten Lauf auf eine Sekunde und verlangt in der Simulator-Karte eine Startbestaetigung.
- Laesst die normale Dashboard-Simulation weiterhin vollstaendig ohne Lichtbefehle laufen.
- Erhoeht die Home-Assistant-Manifest-Version auf `26.5.23-beta.15`.

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
