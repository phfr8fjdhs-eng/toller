# Baustellen-Dashboard

## Was wird gebaut
Ein **echtes Dashboard für eine Firma, die Gartenbau, Strassenbau und Tiefbau zusammen macht**.
Sachlich aufgebaut, kein Spiel: Karte, Baustellen als Marker, Maschinen mit Status,
Alarm bei Störung (Banner und Blinken), Einsatzbereitschaft als Kennzahl.
Man sieht sofort: wo wird gearbeitet, welche Maschine läuft, wartet oder ist kaputt,
und was fehlt (Material oder Diesel als Meldung an der Maschine, alles andere als frei geschriebener Bedarf auf der Baustelle).
Viele Handys sind gleichzeitig verbunden und sehen denselben Stand.

## Begriffe
- **Sparte:** `garten` (Gartenbau), `strasse` (Strassenbau), `tief` (Tiefbau)
- **Baustelle:** Ort auf der Karte mit Maschinen und einer Bedarfsliste
- **Bedarf:** frei geschriebener Text je Baustelle, was gebraucht wird (z. B. "20 m³ Kies bis Mittwoch"). Alle Freigegebenen schreiben und haken ab. Keine Mengen in Prozent
- **Modus:** `leicht` (ohne Karte und 3D, für ältere Handys) oder `3d` (Karte und 3D-Ansicht der Baustelle, für Computer)
- **Werkhof:** Standort für Maschinen, die gerade nicht im Einsatz sind (feste Position aus `public/config.js`, keine Datenbank-Zeile)
- **Maschine:** Bagger, Walze, Fertiger, Dumper, LKW, Radlader usw.
- **Freigabe:** Neue Benutzer sehen nichts, bis ein Admin sie freigibt

## Technik
- Reines HTML, CSS und JavaScript: `public/index.html` (Seite) und `public/config.js` (Einstellungen). Kein Build-Schritt.
- Datenbank, Login und Echtzeit: Supabase (supabase-js von unpkg). Schema: `supabase/schema.sql`, Beispieldaten: `supabase/beispieldaten.sql`. Einrichtung: `SUPABASE-ANLEITUNG.md`
- **Demo und Live:** Ohne `supabaseUrl` und `supabaseKey` in `config.js` läuft der **Demo-Modus** (erfundene Daten, lokale Simulation, nichts wird gespeichert). Mit Werten läuft der **Live-Modus**
- **Leicht und 3D (Anzeige-Modus, unabhängig von Demo/Live):** Beim ersten Öffnen wählt `detectMode()` nach Gerät (kleiner Bildschirm, wenig Speicher, 2 Kerne, Datensparmodus -> Leicht). Der Knopf "Modus" wechselt, die Wahl wird im Gerät gemerkt, `?modus=leicht` oder `?modus=3d` in der Adresse gewinnt (für Tests). Im Leicht-Modus werden MapLibre und three.js **nie** geladen, Szenen bei vielen Baustellen erst beim Hinscrollen gezeichnet (`lazyScene`)
- Baustellen-Szenen: Skizze und Marker zeigen eine kleine SVG-Szene je Baustelle (Boden nach Sparte, Silhouetten nach Maschinenart, Bedarfstafel bei offenem Bedarf), gebaut in `buildScene`
- **3D-Ansicht einer Baustelle** (nur Modus 3D, Knopf "3D-Ansicht" in der Detailansicht): three.js 0.147.0 und OrbitControls von unpkg, erst beim Öffnen geladen. Jede Maschine ist aus einfachen Körpern gebaut (`MODELS3`), der Boden hängt von Sparte und Maschinen ab (`ground3`). Status als Ring und Leuchte in den Status-Farben plus Text am Namensschild, Bedarfstafel mit den offenen Texten (nur `fillText`). Höchstens 24 Maschinen gezeigt (mit Hinweis). `close3D()` gibt alle Ressourcen frei. Die Version ist absichtlich fest: ab 0.148 gibt es `examples/js` nicht mehr
- 3D-Karte: MapLibre GL JS (unpkg), Stil "positron" von OpenFreeMap (kein Schlüssel), Höhendaten von AWS Terrain Tiles. Ohne Internet bleibt die Skizze als Ersatz
- Adresssuche beim Anlegen einer Baustelle: swisstopo SearchServer (kostenlos). Noch nicht gegen den echten Dienst getestet
- Gebiet: Rapperswil-Jona und Umgebung. Die Karte muss auf Handys flüssig laufen, darum bewusst schlank (kein 3D-Gebäude-Modell, Schalter "3D" für 2D-Ansicht, kompakte Marker bei weitem Zoom)
- Veröffentlichung: Netlify veröffentlicht nur den Ordner `public` (siehe `netlify.toml`). Nur Dateien, die jeder sehen darf, gehören dort hinein. `CLAUDE.md`, Anleitungen, `supabase`, `tests` und `.claude` bleiben ausserhalb

## Datenmodell (Datenbank)
- `profiles`: `id`, `email`, `name`, `role` (`admin` oder `mitarbeiter`), `approved`
- `sites` (Baustellen): `id`, `name`, `sparte`, `lat`, `lng`
- `machines`: `id`, `name`, `typ`, `sparte`, `site_id` (leer = Werkhof), `status` (`running`, `waiting`, `broken`, `off`), `reason` (bei `waiting`: "Material fehlt" oder "Diesel fehlt")
- `needs` (Bedarf): `id`, `site_id`, `text`, `created_by`, `created_at`, `done`, `done_by`. Freigegebene lesen, schreiben und haken ab (ein Trigger `needs_guard` lässt Nicht-Admins nur `done` und `done_by` ändern), löschen dürfen der Schreiber und Admins
- `activity` (Protokoll): `id`, `created_at`, `user_id`, `text`
- In der Seite werden Zeilen auf Objekte mit `site` umgeschrieben (`mapSite`, `mapMachine`, `mapNeed`)
- Alte Datenbanken haben noch die unbenutzten Spalten `material_name`, `material_level` und `tank`. Sie schaden nicht (Standardwerte) und lassen sich optional entfernen (siehe `SUPABASE-ANLEITUNG.md`)
- Fehlt die Tabelle `needs` (schema.sql noch nicht erneut ausgeführt), läuft die Seite weiter und zeigt beim Bedarf einen Hinweis (`needsOk`)

## Regeln
- Status-Farben immer gleich: grün = läuft, gelb = wartet (Material oder Diesel fehlt), rot blinkend = kaputt, grau = im Werkhof
- Sparten nie mit Status-Farben markieren: Sparte nur als Buchstaben-Tag (G, S, T)
- Eine Baustelle zeigt immer den schlechtesten Status ihrer Maschinen
- **Kein Ton, nie.** Eine neue Störung (Wechsel auf `broken`) wird einmal gezählt und als Banner und rot blinkende Maschine gezeigt, auch bei Störungen von anderen Handys
- Sicherheit liegt in der Datenbank (Row Level Security in `schema.sql`), nicht in der Seite. Die Seite blendet nur Knöpfe aus. Jede Änderung an Tabellen braucht passende Regeln und einen Test
- Der `anon`-Key darf in `config.js` stehen. Den `service_role`-Key und Passwörter nie in Code, Chat oder Repo (gehören in `.env`, die in `.gitignore` steht)
- Texte aus Benutzereingaben nur mit `textContent` anzeigen, nie mit `innerHTML`
- Automatisches Neuzeichnen (`softRender`) wartet, solange ein Finger gedrückt ist, sonst gehen Klicks verloren
- Löschen mit Zwei-Schritt-Knopf (`confirmBtn`), nicht mit `confirm()`
- Die Anzeige ist ein Arbeitswerkzeug einer Firma: sachlich, keine Spielelemente, und die Zahlen müssen echt und ehrlich sein (kein Schönfärben)
- **Keine Prozentanzeigen für Material, Diesel oder Baustellen.** Material und Wünsche stehen als frei geschriebener Bedarf auf der Baustelle, Diesel ist nur die Meldung "Diesel fehlt". Einzige Prozentzahl: die Einsatzbereitschaft (Anteil laufender Maschinen im Einsatz, eine echte Zählung)
- Im 3D-Fenster gilt dasselbe wie sonst: Status nie nur über die Farbe (Text am Schild), Störung auch als Banner im Fenster, Sparte nur durch den Boden und den Buchstaben-Tag, nie in Status-Farben, beim Schliessen alles freigeben
- three.js bleibt fest auf Version 0.147.0 (siehe Technik). Eine neue Version braucht ein neues Einbinden der OrbitControls als Modul und einen Test im echten Browser
- Handy zuerst: Bedienung mit dem Finger, grosse Buttons, auf kleinen Bildschirmen keine seitliche Scrollleiste
- Schreibweise Schweiz: "Strassenbau" mit ss
- Kleine Schritte: nach jeder fertigen Funktion ein Commit mit klarer Nachricht auf Deutsch
- Vor größeren Änderungen erst einen Plan zeigen

## Tests
- Alles in `tests/`: `db_test.sh` (Schema und Zugriffsregeln auf lokaler PostgreSQL, braucht Root-Rechte), `app_test.py` (Seite im Browser mit Ersatz-Datenbank aus `stubs.js`, braucht Playwright)
- Vor jedem Hochladen laufen lassen. Die Tests ersetzen nicht den Test gegen echtes Supabase und die echte Karte
- `stubs.js` ersetzt auch three.js: die Tests prüfen, dass je Maschine ein Modell entsteht, Texte auf den Schildern stehen, bei Änderungen neu gebaut und beim Schliessen alles freigegeben wird. **Das echte 3D-Bild (Form der Maschinen, Kamera, Licht, Blinken) ist damit nicht geprüft** und muss einmal auf einem Computer mit echtem WebGL angesehen werden

## Befehle
- Starten: `public/index.html` im Browser öffnen (Demo-Modus)
- Tests: `bash tests/db_test.sh` und `python3 tests/app_test.py`

## Aufgaben für später
- Erster Test gegen ein echtes Supabase-Projekt (Anmeldung, Freigabe, Echtzeit, Adresssuche, Tabelle needs)
- 3D-Ansicht einmal mit echtem WebGL ansehen und die Maschinenmodelle verfeinern (three.js konnte in der Entwicklungsumgebung nicht geladen werden)
- Standort der Mitarbeiter oder Maschinen auf der Baustelle: **noch nicht gebaut**, offene Fragen zuerst klären (Personen oder Maschinen, wer sieht es, Einwilligung und Datenschutz, nur aktuelle Position, Information der Mitarbeiter)
- **Excel-Anbindung (bewusst später):** Excel-Tabellen mit Baustellen, Maschinen und Status sollen automatisch eingelesen werden. Entscheidungen: Excel liefert auch den Status, Excel ist dann die Quelle der Wahrheit für seine Zeilen (Handy darf diese Status nicht ändern), im Dashboard angelegte Zeilen bleiben erhalten, der Sync fasst nur Excel-Zeilen an. Datei in SharePoint/OneDrive, Sync als zeitgesteuerte Funktion in der Cloud, Leserecht nur auf eine Datei über Microsoft Graph. Die IT muss die App-Registrierung anlegen. Vorher Beispieldatei ansehen
- Passwort-vergessen-Knopf
- Push-Nachrichten aufs Handy bei Störung (die Seite zeigt nur etwas, solange sie offen ist)
- Kartenanbieter für den Firmenbetrieb festlegen (Bedingungen von OpenFreeMap prüfen, Alternativen: swisstopo oder bezahlter Anbieter)
- Supabase-Plan und Datenschutz für den Firmenbetrieb klären (Region, Backups, Pausierung)
- Mehr als 1000 Baustellen oder Maschinen: Abfragen in Seiten teilen
- Optional: 3D-Gebäude und feineres Gelände, nur wenn es auf Handys flüssig bleibt
- Verlauf der Störungen und Auswertung
