# Baustellen-Dashboard

## Was wird gebaut
Ein **echtes Dashboard für eine Firma, die Gartenbau, Strassenbau und Tiefbau zusammen macht**.
Sachlich aufgebaut, kein Spiel: Karte, Baustellen als Marker, Maschinen mit Status,
Alarm bei Störung (Banner und Blinken), Einsatzbereitschaft als Kennzahl.
Man sieht sofort: wo wird gearbeitet, welche Maschine läuft, wartet oder ist kaputt,
und was fehlt (Material oder Diesel als Meldung an der Maschine, alles andere als frei geschriebener Bedarf auf der Baustelle).
Viele Handys sind gleichzeitig verbunden und sehen denselben Stand.

## Begriffe
- **Sparte:** `garten` (Gartenbau), `strasse` (Strassenbau), `tief` (Tiefbau). Eine Baustelle hat eine **Hauptsparte** (bestimmt den Boden in Szene und 3D) und beliebig viele **weitere Sparten** (z. B. Strassenbau + Tiefbau). Anzeige als Buchstaben `S T`, Hauptsparte zuerst. Der Filter zeigt eine Baustelle, wenn eine ihrer Sparten gewählt ist (`showSite`). Eine Maschine hat genau eine Sparte
- **Baustelle:** Ort auf der Karte mit Maschinen und einer Bedarfsliste
- **Materialmeldung:** Tipp auf "Material fehlt" an einer Maschine öffnet eine Auswahl aus dem Katalog (`public/materialien.js`, über 450 übliche Bezeichnungen mit Suche und Kategorie). Jede freigegebene Person darf zusätzlich ein eigenes Material eintippen, es wird in `materials` gespeichert und steht allen zur Auswahl. Dazu ein freies Feld für Menge oder Hinweis (nie Prozent). Grund der Maschine: `Material fehlt: Kies 0/32` oder `Material fehlt: Kies 0/32 · ca. 20 m³`
- **Absender:** Bei jeder Meldung (Defekt, Material fehlt, Diesel fehlt) steht, wer sie abgeschickt hat und wann. Name und Zeit setzt die Datenbank (Trigger `machines_stamp`), nicht die Seite
- **Bedarf:** frei geschriebener Text je Baustelle, was gebraucht wird (z. B. "20 m³ Kies bis Mittwoch"). Alle Freigegebenen schreiben und haken ab. Keine Mengen in Prozent
- **Modus:** `leicht` (ohne Karte und 3D, für ältere Handys) oder `3d` (Karte und 3D-Ansicht der Baustelle, für Computer)
- **Werkhof:** Standort für Maschinen, die gerade nicht im Einsatz sind (feste Position aus `public/config.js`, keine Datenbank-Zeile)
- **Maschine:** Bagger, Walze, Fertiger, Dumper, LKW, Radlader usw.
- **Freigabe:** Neue Benutzer sehen nichts, bis ein Admin sie freigibt

## Technik
- Reines HTML, CSS und JavaScript: `public/index.html` (Seite), `public/config.js` (Einstellungen) und `public/materialien.js` (Materialkatalog, nur Namen, keine Firmendaten). Kein Build-Schritt.
- Datenbank, Login und Echtzeit: Supabase (supabase-js von unpkg). Schema: `supabase/schema.sql`, Beispieldaten: `supabase/beispieldaten.sql`. Einrichtung: `SUPABASE-ANLEITUNG.md`
- **Demo und Live:** Ohne `supabaseUrl` und `supabaseKey` in `config.js` läuft der **Demo-Modus** (erfundene Daten, lokale Simulation, nichts wird gespeichert). Mit Werten läuft der **Live-Modus**
- **Leicht und 3D (Anzeige-Modus, unabhängig von Demo/Live):** Beim ersten Öffnen wählt `detectMode()` nach Gerät (kleiner Bildschirm, wenig Speicher, 2 Kerne, Datensparmodus -> Leicht). Der Knopf "Modus" wechselt, die Wahl wird im Gerät gemerkt, `?modus=leicht` oder `?modus=3d` in der Adresse gewinnt (für Tests). Im Leicht-Modus werden MapLibre und three.js **nie** geladen, Szenen bei vielen Baustellen erst beim Hinscrollen gezeichnet (`lazyScene`)
- Baustellen-Szenen: Skizze und Marker zeigen eine kleine SVG-Szene je Baustelle (Boden nach Sparte, Silhouetten nach Maschinenart, Bedarfstafel bei offenem Bedarf), gebaut in `buildScene`
- **3D-Ansicht einer Baustelle** (nur Modus 3D, Knopf "3D-Ansicht" in der Detailansicht): three.js 0.147.0 und OrbitControls von unpkg, erst beim Öffnen geladen. Jede Maschine ist aus einfachen Körpern gebaut (`MODELS3`), der Boden hängt von Sparte und Maschinen ab (`ground3`). Status als Ring und Leuchte in den Status-Farben plus Text am Namensschild, Bedarfstafel mit den offenen Texten (nur `fillText`). Höchstens 24 Maschinen gezeigt (mit Hinweis). `close3D()` gibt alle Ressourcen frei. Die Version ist absichtlich fest: ab 0.148 gibt es `examples/js` nicht mehr
- 3D-Karte: MapLibre GL JS (unpkg), Stil "positron" von OpenFreeMap (kein Schlüssel), Höhendaten von AWS Terrain Tiles. Ohne Internet bleibt die Skizze als Ersatz
- Adresssuche beim Anlegen einer Baustelle: swisstopo SearchServer (kostenlos). Noch nicht gegen den echten Dienst getestet
- **Baustelle aus Offerte oder Beschreibung (nur Admin, in der Seite):** Im Fenster "Neue Baustelle" fügt der Admin Text ein, `parseOffer` schlägt Name, Sparte, Adressen und Bedarfszeilen vor (reiner Text, keine Bibliothek, kein PDF-Lesen). Die erste Adresse wird über swisstopo gesucht und als Ort vorgeschlagen, weitere Adressen aus dem Text stehen als Knopf zur Wahl (der Absender der Offerte steht oft im Kopf). Der Admin prüft und wählt Zeilen ab oder ändert sie. Gespeichert wird nur das Gewählte: Baustelle und Bedarf (`addNeeds`, ein Speichern). **Preise, Summen und Kundendaten werden entfernt, der Rohtext wird nie gespeichert.** Eine geratene erste Zeile ersetzt nie einen getippten Namen. Die Rechte in der Datenbank sind unverändert (Baustellen und Bedarf dürfen alle Freigegebenen anlegen), das Feld ist nur für Admins sichtbar. Der Parser nutzt bewusst keine neueren Sprachmittel (`\p{L}`, Lookbehind), damit alte Handys die Seite weiter laden
- **Speicher auf dem Handy ist wichtig:** Neue Funktionen laden erst bei Gebrauch, ohne Bibliotheken, Fenster werden beim Schliessen entfernt. `tests/speicher_test.py` misst Heap und Seitenelemente im Leicht-Modus (60 Baustellen, 180 Maschinen) und hält Grenzen ein. Gemessen ist nur der JavaScript-Heap, nicht Grafikspeicher
- Gebiet: Rapperswil-Jona und Umgebung. Die Karte gibt es nur im Modus 3D (Computer), Handys im Modus Leicht laden sie nie
- **Baustellen sind Teil der Karte** (keine Kärtchen mit Bild auf der Karte): Fläche und Rand in der Statusfarbe ab Zoom 13 (`site-fill`, `site-line`, Kreis mit `SITE_R` Metern um den Punkt), weit weg ein Punkt (`site-dot`), Schrift mit Sparten-Buchstabe und Name, nah zusätzlich Status, Maschinen und Bedarf (`site-label`, feste Schriftgrösse). Gestört = Rand blinkt rot. Antippen öffnet die Details. Daten aus `siteGeo()`, aktualisiert mit `syncMapSites()`
- **Maschinen auf der Karte** (ab Zoom 14.5): Bild je Maschinenart und Status (`machIconUrl`, Silhouette aus `machShape`, Ring in der Statusfarbe, 44 Bilder beim Laden der Karte), Name und bei Störung das Wort "Defekt" bzw. der Grund. Defekt blinkt. Verteilt in einer Spirale um die Mitte der Baustelle oder des gezeichneten Bereichs (`machineGeo`), **nur eine Anordnung, nicht der echte Standort**. Antippen öffnet die Baustelle
- **Zeichnen auf der Karte** (nur Modus 3D, Knopf "Zeichnen" in der Detailansicht, `modalDraw`, `startDrawing`, Leiste `drawBar`): Linien (Strasse/Weg, Wasser, Abwasser, Gas, Strom, Kabel, Hecke), Punkte (Baum, jeder Tipp ein Baum), Flächen (Baustellenbereich, Rasen/Pflanzfläche schraffiert, Belag). Arten in `DRAW_KINDS`, Farben sind **nie Statusfarben**, Linien tragen ihren Namen als Schrift. Länge/Fläche aus der Zeichnung (`drawingMeasure`, immer "ca."). Ein gezeichneter Baustellenbereich ersetzt den Kreis. Liste "Auf der Karte" in der Detailansicht (auch Leicht). Bei Leitungen steht immer der Hinweis, dass die Zeichnung keinen Werkleitungsplan ersetzt
- 3D-Häuser aus den OpenFreeMap-Daten (OpenStreetMap-Höhen, `render_height`), Ebene `bauten`, erst ab Zoom 14. Einfache Blöcke, Höhe fehlt teilweise (dann 8 m)
- Die helle Grundkarte wird beim Laden dunkel umgefärbt (`darkenBasemap`). Kein CSS-Filter auf der Karte, sonst stimmen die Statusfarben nicht mehr
- Veröffentlichung: Netlify veröffentlicht nur den Ordner `public` (siehe `netlify.toml`). Nur Dateien, die jeder sehen darf, gehören dort hinein. `CLAUDE.md`, Anleitungen, `supabase`, `tests` und `.claude` bleiben ausserhalb

## Datenmodell (Datenbank)
- `profiles`: `id`, `email`, `name`, `role` (`admin` oder `mitarbeiter`), `approved`
- `sites` (Baustellen): `id`, `name`, `sparte` (Hauptsparte), `weitere_sparten` (text[], nur `garten`/`strasse`/`tief`, der Trigger `sites_sparten` entfernt Doppelte und die Hauptsparte und ordnet), `lat`, `lng`. In der Seite: `extra`, Hilfen `spartenOf`, `spartenTag`, `spartenText`. Ändern über "Sparten ändern" in der Detailansicht (`modalSparten`, alle Freigegebenen). Fehlt die Spalte (schema.sql nicht erneut ausgeführt), läuft alles mit der Hauptsparte weiter und zeigt einen Hinweis (`spartenOk`)
- `machines`: `id`, `name`, `typ`, `sparte`, `site_id` (leer = Werkhof), `status` (`running`, `waiting`, `broken`, `off`), `reason` (bei `waiting`: `Material fehlt: <Material>` mit optionalem ` · <Hinweis>`, oder `Diesel fehlt`), `reported_by`, `reported_name`, `reported_at` (Absender und Zeit der Meldung, nur vom Trigger `machines_stamp` gesetzt: neue Meldung = aktuelle Person, läuft wieder oder Werkhof = leer, sonst unverändert)
- `materials` (eigene Materialien der Mitarbeiter, zusätzlich zum Katalog in `materialien.js`): `id`, `name` (2 bis 60 Zeichen, eindeutig ohne Gross/Klein), `author` (setzt der Trigger `materials_stamp`), `created_by`, `created_at`. Freigegebene lesen und schreiben, nichts ändern, löschen dürfen der Schreiber und Admins
- `needs` (Bedarf): `id`, `site_id`, `text`, `created_by`, `created_at`, `done`, `done_by`. Freigegebene lesen, schreiben und haken ab (ein Trigger `needs_guard` lässt Nicht-Admins nur `done` und `done_by` ändern), löschen dürfen der Schreiber und Admins
- `activity` (Protokoll): `id`, `created_at`, `user_id`, `text`
- `drawings` (Zeichnungen auf der Karte): `id`, `site_id` (löscht mit der Baustelle), `kind`, `geom` (GeoJSON, `[Längengrad, Breitengrad]`), `label` (bis 60 Zeichen), `author` (setzt der Trigger `drawings_stamp`), `created_by`, `created_at`. Die Prüfung `drawing_ok` lässt nur passende Geometrie zu (Baum = Punkt, Linien 2 bis 500 Punkte, Flächen ein geschlossener Ring). Freigegebene lesen und zeichnen, **nie ändern** (löschen und neu zeichnen), löschen dürfen der Zeichner und Admins. Fehlt die Tabelle, läuft die Seite mit Hinweis weiter (`drawingsOk`)
- `downtimes` (Verlauf der Störungen und Wartezeiten): `id`, `machine_id` (leer, wenn die Maschine gelöscht wurde), `machine_name`, `typ`, `site_name` (Kopien, damit der Verlauf lesbar bleibt), `kind` (`broken` oder `waiting`), `reason`, `reported_name`, `started_at`, `ended_at` (leer = noch offen). **Nur der Trigger `downtimes_track` schreibt** (Beginn = Meldung, Ende = Repariert, Nachgeliefert, Getankt oder Maschine gelöscht). Niemand schreibt von Hand, auch kein Admin: kein Schönfärben. Freigegebene dürfen lesen. Nur ein offener Eintrag je Maschine. Anderer Hinweis zum selben Material ist dieselbe Wartezeit. Die Zeiten zeigen, wie lange eine Meldung offen war, nicht eine Messung an der Maschine. Der Eintrag enthält den Namen der meldenden Person (wie an der Maschine)
- Knopf "Tabellen" (alle Freigegebenen): `modalTables` mit zwei Reitern. **Baustellen:** Status (Punkt und Text), Sparten, Name, Maschinen (Anzahl je Status und Namen), offener Bedarf. **Maschinen:** Status, Name, Art, Sparte, Wo (Baustelle oder Werkhof), Grund, gemeldet von und wann. Sortieren per Spaltenkopf (Handy: Auswahl `tblSort`), Suche, der Sparten-Filter gilt. Zeile antippen öffnet die Baustelle. Wird erst beim Öffnen gebaut, läuft live mit (`tablesRefresh` aus `render`), höchstens `TBL_MAX` Zeilen mit Hinweis. Am Handy werden Zeilen zu Karten (keine seitliche Scrollleiste)
- Knopf "Verlauf" (alle Freigegebenen): `modalHistory` lädt erst beim Öffnen, höchstens 500 Einträge, zeigt je Art Anzahl und Dauer, je Maschine (längste Dauer zuerst) und die Einträge (40, dann "Weitere anzeigen"). Keine Prozentzahlen, Art als Text (nicht nur Farbe). Fehlt die Tabelle, steht ein Hinweis zum Datenbank-Update. Demo: lokale Liste dieser Sitzung (`demoDowntimes`)
- In der Seite werden Zeilen auf Objekte mit `site`, `by`, `at` umgeschrieben (`mapSite`, `mapMachine`, `mapNeed`, `mapMaterial`)
- Alte Datenbanken haben noch die unbenutzten Spalten `material_name`, `material_level` und `tank`. Sie schaden nicht (Standardwerte) und lassen sich optional entfernen (siehe `SUPABASE-ANLEITUNG.md`)
- Fehlt die Tabelle `needs` oder `materials` (schema.sql noch nicht erneut ausgeführt), läuft die Seite weiter und zeigt einen Hinweis (`needsOk`, `matsOk`). Fehlen nur die Spalten `reported_*`, wird kein Absender gezeigt

## Regeln
- Status-Farben immer gleich: grün = läuft, gelb = wartet (Material oder Diesel fehlt), rot blinkend = kaputt, grau = im Werkhof
- Sparten nie mit Status-Farben markieren: Sparte nur als Buchstaben-Tag (G, S, T, bei mehreren z. B. `S T`)
- Eine Baustelle zeigt immer den schlechtesten Status ihrer Maschinen
- **Kein Ton, nie.** Eine neue Störung (Wechsel auf `broken`) wird einmal gezählt und als Banner und rot blinkende Maschine gezeigt, auch bei Störungen von anderen Handys
- Sicherheit liegt in der Datenbank (Row Level Security in `schema.sql`), nicht in der Seite. Die Seite blendet nur Knöpfe aus. Jede Änderung an Tabellen braucht passende Regeln und einen Test
- Der `anon`-Key darf in `config.js` stehen. Den `service_role`-Key und Passwörter nie in Code, Chat oder Repo (gehören in `.env`, die in `.gitignore` steht)
- Texte aus Benutzereingaben nur mit `textContent` anzeigen, nie mit `innerHTML`
- Automatisches Neuzeichnen (`softRender`) wartet, solange ein Finger gedrückt ist, sonst gehen Klicks verloren
- Löschen mit Zwei-Schritt-Knopf (`confirmBtn`), nicht mit `confirm()`
- Die Anzeige ist ein Arbeitswerkzeug einer Firma: sachlich, keine Spielelemente, und die Zahlen müssen echt und ehrlich sein (kein Schönfärben)
- Materialnamen und Hinweise aus Benutzereingaben (Auswahl, eigener Eintrag, Hinweis) nur mit `textContent` zeigen. Ein eigener Eintrag entsteht nur durch den ausdrücklichen Tipp auf "neu hinzufügen", nie durch Enter oder aus Versehen. Nachgeliefert gibt nur Maschinen frei, die auf dasselbe Material warten (der Status muss ehrlich bleiben)
- **Keine Prozentanzeigen für Material, Diesel oder Baustellen.** Material und Wünsche stehen als frei geschriebener Bedarf auf der Baustelle, Diesel ist nur die Meldung "Diesel fehlt". Einzige Prozentzahl: die Einsatzbereitschaft (Anteil laufender Maschinen im Einsatz, eine echte Zählung)
- Zeichnungen sind eine Skizze zur Übersicht, keine Vermessung. Gezeichnete Leitungen immer mit dem Hinweis, dass sie keinen Werkleitungsplan ersetzen
- Im 3D-Fenster gilt dasselbe wie sonst: Status nie nur über die Farbe (Text am Schild), Störung auch als Banner im Fenster, Sparte nur durch den Boden und den Buchstaben-Tag, nie in Status-Farben, beim Schliessen alles freigeben
- three.js bleibt fest auf Version 0.147.0 (siehe Technik). Eine neue Version braucht ein neues Einbinden der OrbitControls als Modul und einen Test im echten Browser
- Handy zuerst: Bedienung mit dem Finger, grosse Buttons, auf kleinen Bildschirmen keine seitliche Scrollleiste
- Schreibweise Schweiz: "Strassenbau" mit ss
- Kleine Schritte: nach jeder fertigen Funktion ein Commit mit klarer Nachricht auf Deutsch
- Vor größeren Änderungen erst einen Plan zeigen

## Tests
- Alles in `tests/`: `db_test.sh` (Schema und Zugriffsregeln auf lokaler PostgreSQL, braucht Root-Rechte), `app_test.py` (Seite im Browser mit Ersatz-Datenbank aus `stubs.js`, braucht Playwright), `speicher_test.py` (Heap und Seitenelemente im Leicht-Modus, braucht Playwright)
- Vor jedem Hochladen laufen lassen. Die Tests ersetzen nicht den Test gegen echtes Supabase und die echte Karte
- Die Browser-Tests laufen ohne Zufall (`Math.random` ist festgelegt), weil die Demo sonst von selbst Störungen meldet und Ergebnisse schwanken. Die Simulation prüft ein eigener Test
- `stubs.js` ersetzt auch three.js: die Tests prüfen, dass je Maschine ein Modell entsteht, Texte auf den Schildern stehen, bei Änderungen neu gebaut und beim Schliessen alles freigegeben wird. **Das echte 3D-Bild (Form der Maschinen, Kamera, Licht, Blinken) ist damit nicht geprüft** und muss einmal auf einem Computer mit echtem WebGL angesehen werden

## Befehle
- Starten: `public/index.html` im Browser öffnen (Demo-Modus)
- Tests: `bash tests/db_test.sh`, `python3 tests/app_test.py` und `python3 tests/speicher_test.py`

## Aufgaben für später
- Erster Test gegen ein echtes Supabase-Projekt (Anmeldung, Freigabe, Echtzeit, Adresssuche, Tabellen needs und materials, Absender an Meldungen)
- Materialkatalog von der Firma prüfen und anpassen lassen (`public/materialien.js` ist eine Vorschlagsliste mit üblichen Bezeichnungen, von Claude zusammengestellt)
- 3D-Ansicht einmal mit echtem WebGL ansehen und die Maschinenmodelle verfeinern (three.js konnte in der Entwicklungsumgebung nicht geladen werden)
- Standort der Mitarbeiter oder Maschinen auf der Baustelle: **noch nicht gebaut**, offene Fragen zuerst klären (Personen oder Maschinen, wer sieht es, Einwilligung und Datenschutz, nur aktuelle Position, Information der Mitarbeiter)
- **Excel-Anbindung (bewusst später):** Excel-Tabellen mit Baustellen, Maschinen und Status sollen automatisch eingelesen werden. Entscheidungen: Excel liefert auch den Status, Excel ist dann die Quelle der Wahrheit für seine Zeilen (Handy darf diese Status nicht ändern), im Dashboard angelegte Zeilen bleiben erhalten, der Sync fasst nur Excel-Zeilen an. Datei in SharePoint/OneDrive, Sync als zeitgesteuerte Funktion in der Cloud, Leserecht nur auf eine Datei über Microsoft Graph. Die IT muss die App-Registrierung anlegen. Vorher Beispieldatei ansehen
- Passwort-vergessen ist gebaut (Mail-Link, dann "Neues Passwort"), aber **noch nicht gegen echtes Supabase getestet**: Site URL und Redirect URLs setzen, eigenen Mail-Server (SMTP) einrichten, einmal von Anfang bis Ende durchspielen
- Push-Nachrichten aufs Handy bei Störung (die Seite zeigt nur etwas, solange sie offen ist)
- Kartenanbieter für den Firmenbetrieb festlegen (Bedingungen von OpenFreeMap prüfen, Alternativen: swisstopo oder bezahlter Anbieter)
- Supabase-Plan und Datenschutz für den Firmenbetrieb klären (Region, Backups, Pausierung)
- Mehr als 1000 Baustellen oder Maschinen: Abfragen in Seiten teilen
- Genauere 3D-Gebäude von swisstopo prüfen (offizielle Daten statt OpenStreetMap)
- Maschinen genau auf der Karte platzieren (heute nur automatisch verteilt)
- Zeichnungen bearbeiten (heute nur löschen und neu zeichnen), Linie automatisch der Strasse folgen lassen (bräuchte einen Routendienst)
- Auswertung des Verlaufs ausbauen (Wochenbericht, Export, Vergleich der Maschinen). Der Verlauf selbst ist gebaut. Offen: wie lange Daten aufbewahrt werden (Datenschutz, Namen der Meldenden) und ob Kopien gelöscht werden sollen
