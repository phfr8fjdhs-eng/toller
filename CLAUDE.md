# Baustellen-Dashboard

## Was wird gebaut
Ein **echtes Dashboard für eine Firma, die Gartenbau, Strassenbau und Tiefbau zusammen macht**.
Aufgebaut wie ein Spiel: Karte von oben, Baustellen als Marker, Maschinen mit Status,
Alarm bei Störung, Lebensleiste für die Einsatzbereitschaft.
Man sieht sofort: wo wird gearbeitet, welche Maschine läuft, wartet oder ist kaputt,
und was fehlt (Material oder Diesel).
Viele Handys sind gleichzeitig verbunden und sehen denselben Stand.

## Begriffe
- **Sparte:** `garten` (Gartenbau), `strasse` (Strassenbau), `tief` (Tiefbau)
- **Baustelle:** Ort auf der Karte mit Maschinen und einem Hauptmaterial (z. B. Asphalt, Kies, Humus, Pflanzen)
- **Werkhof:** Standort für Maschinen, die gerade nicht im Einsatz sind (feste Position aus `public/config.js`, keine Datenbank-Zeile)
- **Maschine:** Bagger, Walze, Fertiger, Dumper, LKW, Radlader usw.
- **Freigabe:** Neue Benutzer sehen nichts, bis ein Admin sie freigibt

## Technik
- Reines HTML, CSS und JavaScript: `public/index.html` (Seite) und `public/config.js` (Einstellungen). Kein Build-Schritt.
- Datenbank, Login und Echtzeit: Supabase (supabase-js von unpkg). Schema: `supabase/schema.sql`, Beispieldaten: `supabase/beispieldaten.sql`. Einrichtung: `SUPABASE-ANLEITUNG.md`
- **Zwei Modi:** Ohne `supabaseUrl` und `supabaseKey` in `config.js` läuft der **Demo-Modus** (erfundene Daten, lokale Simulation, nichts wird gespeichert). Mit Werten läuft der **Live-Modus**
- 3D-Karte: MapLibre GL JS (unpkg), Stil "positron" von OpenFreeMap (kein Schlüssel), Höhendaten von AWS Terrain Tiles. Ohne Internet bleibt die Skizze als Ersatz
- Adresssuche beim Anlegen einer Baustelle: swisstopo SearchServer (kostenlos). Noch nicht gegen den echten Dienst getestet
- Gebiet: Rapperswil-Jona und Umgebung. Die Karte muss auf Handys flüssig laufen, darum bewusst schlank (kein 3D-Gebäude-Modell, Schalter "3D" für 2D-Ansicht, kompakte Marker bei weitem Zoom)
- Veröffentlichung: Netlify veröffentlicht nur den Ordner `public` (siehe `netlify.toml`). Nur Dateien, die jeder sehen darf, gehören dort hinein. `CLAUDE.md`, Anleitungen, `supabase`, `tests` und `.claude` bleiben ausserhalb

## Datenmodell (Datenbank)
- `profiles`: `id`, `email`, `name`, `role` (`admin` oder `mitarbeiter`), `approved`
- `sites` (Baustellen): `id`, `name`, `sparte`, `material_name`, `material_level` (0-100), `lat`, `lng`
- `machines`: `id`, `name`, `typ`, `sparte`, `site_id` (leer = Werkhof), `status` (`running`, `waiting`, `broken`, `off`), `tank` (0-100), `reason`
- `activity` (Protokoll): `id`, `created_at`, `user_id`, `text`
- In der Seite werden Zeilen auf Objekte mit `site`, `material:{name,level}` umgeschrieben (`mapSite`, `mapMachine`)

## Regeln
- Status-Farben immer gleich: grün = läuft, gelb = wartet (Material oder Diesel fehlt), rot blinkend = kaputt, grau = im Werkhof
- Sparten nie mit Status-Farben markieren: Sparte nur als Buchstaben-Tag (G, S, T)
- Eine Baustelle zeigt immer den schlechtesten Status ihrer Maschinen
- Warnton nur einmal pro neuer Störung (Wechsel auf `broken`), nicht dauerhaft. Auch bei Störungen von anderen Handys
- Sicherheit liegt in der Datenbank (Row Level Security in `schema.sql`), nicht in der Seite. Die Seite blendet nur Knöpfe aus. Jede Änderung an Tabellen braucht passende Regeln und einen Test
- Der `anon`-Key darf in `config.js` stehen. Den `service_role`-Key und Passwörter nie in Code, Chat oder Repo (gehören in `.env`, die in `.gitignore` steht)
- Texte aus Benutzereingaben nur mit `textContent` anzeigen, nie mit `innerHTML`
- Automatisches Neuzeichnen (`softRender`) wartet, solange ein Finger gedrückt ist, sonst gehen Klicks verloren
- Löschen mit Zwei-Schritt-Knopf (`confirmBtn`), nicht mit `confirm()`
- Anzeige darf wie ein Spiel aussehen, die Zahlen müssen aber echt und ehrlich sein (kein Schönfärben)
- Handy zuerst: Bedienung mit dem Finger, grosse Buttons, auf kleinen Bildschirmen keine seitliche Scrollleiste
- Schreibweise Schweiz: "Strassenbau" mit ss
- Kleine Schritte: nach jeder fertigen Funktion ein Commit mit klarer Nachricht auf Deutsch
- Vor größeren Änderungen erst einen Plan zeigen

## Tests
- Alles in `tests/`: `db_test.sh` (Schema und Zugriffsregeln auf lokaler PostgreSQL, braucht Root-Rechte), `app_test.py` (Seite im Browser mit Ersatz-Datenbank aus `stubs.js`, braucht Playwright)
- Vor jedem Hochladen laufen lassen. Die Tests ersetzen nicht den Test gegen echtes Supabase und die echte Karte

## Befehle
- Starten: `public/index.html` im Browser öffnen (Demo-Modus)
- Tests: `bash tests/db_test.sh` und `python3 tests/app_test.py`

## Aufgaben für später
- Erster Test gegen ein echtes Supabase-Projekt (Anmeldung, Freigabe, Echtzeit, Adresssuche)
- **Excel-Anbindung (bewusst später):** Excel-Tabellen mit Baustellen, Maschinen und Status sollen automatisch eingelesen werden. Entscheidungen: Excel liefert auch den Status, Excel ist dann die Quelle der Wahrheit für seine Zeilen (Handy darf diese Status nicht ändern), im Dashboard angelegte Zeilen bleiben erhalten, der Sync fasst nur Excel-Zeilen an. Datei in SharePoint/OneDrive, Sync als zeitgesteuerte Funktion in der Cloud, Leserecht nur auf eine Datei über Microsoft Graph. Die IT muss die App-Registrierung anlegen. Vorher Beispieldatei ansehen
- Passwort-vergessen-Knopf
- Push-Nachrichten aufs Handy bei Störung (Ton im Browser geht nicht bei gesperrtem Handy)
- Kartenanbieter für den Firmenbetrieb festlegen (Bedingungen von OpenFreeMap prüfen, Alternativen: swisstopo oder bezahlter Anbieter)
- Supabase-Plan und Datenschutz für den Firmenbetrieb klären (Region, Backups, Pausierung)
- Mehr als 1000 Baustellen oder Maschinen: Abfragen in Seiten teilen
- Optional: 3D-Gebäude und feineres Gelände, nur wenn es auf Handys flüssig bleibt
- Verlauf der Störungen und Auswertung
