# Baustellen-Dashboard

## Was wird gebaut
Ein **echtes Dashboard für eine Firma, die Gartenbau, Strassenbau und Tiefbau zusammen macht**.
Aufgebaut wie ein Spiel: Karte von oben, Baustellen als Marker, Maschinen mit Status,
Alarm bei Störung, Lebensleiste für die Einsatzbereitschaft.
Man sieht sofort: wo wird gearbeitet, welche Maschine läuft, wartet oder ist kaputt,
und was fehlt (Material oder Diesel).

## Begriffe
- **Sparte:** `garten` (Gartenbau), `strasse` (Strassenbau), `tief` (Tiefbau)
- **Baustelle:** Ort auf der Karte mit Maschinen und einem Hauptmaterial (z. B. Asphalt, Kies, Humus, Pflanzen)
- **Werkhof:** Standort für Maschinen, die gerade nicht im Einsatz sind
- **Maschine:** Bagger, Walze, Fertiger, Dumper, LKW, Radlader usw.

## Technik
- Reines HTML, CSS und JavaScript in `public/index.html` (keine Installation nötig)
- Daten sind jetzt simuliert, später kommen echte Daten über `applyData(list)` rein
- Echte 3D-Karte: MapLibre GL JS (von unpkg) mit dem Stil "positron" von OpenFreeMap (kein Schlüssel nötig) und Höhendaten von AWS Terrain Tiles. Ohne Internet bleibt die Skizze als Ersatz
- Gebiet: Rapperswil-Jona und Umgebung. Die Karte muss auf Handys flüssig laufen, darum bewusst schlank (kein 3D-Gebäude-Modell, Schalter "3D" für 2D-Ansicht)

## Datenmodell
- Maschine: `id`, `name`, `typ`, `sparte`, `site` (Baustellen-Id oder `null` = Werkhof), `status`, `tank` (0-100), `reason`
- Baustelle: `id`, `name`, `sparte`, `material` (`name`, `level` 0-100), `x`, `y` (Prozent auf der Skizze), `lat`, `lng` (echte Position auf der Karte)

## Regeln
- Status-Farben immer gleich: grün = läuft, gelb = wartet (Material oder Diesel fehlt), rot blinkend = kaputt, grau = im Werkhof
- Sparten nie mit Status-Farben markieren: Sparte nur als Buchstaben-Tag (G, S, T)
- Eine Baustelle zeigt immer den schlechtesten Status ihrer Maschinen
- Karte: Baustellen immer mit `lat` und `lng` eintragen. Während ein Finger gedrückt ist, nicht neu zeichnen (sonst gehen Klicks verloren)
- Warnton nur einmal pro neuer Störung, nicht dauerhaft
- Daten und Anzeige getrennt: echte Daten kommen nur über `applyData(list)` rein, die Anzeige (`render`) kennt keine Datenquelle
- Anzeige darf wie ein Spiel aussehen, die Zahlen müssen aber echt und ehrlich sein (kein Schönfärben)
- Mehrere Handys gleichzeitig: alle sehen denselben Stand. Darum braucht es später einen gemeinsamen Datenspeicher mit Echtzeit, nicht nur die lokale Simulation
- Handy zuerst: Bedienung mit dem Finger, grosse Buttons, auf kleinen Bildschirmen eine Liste statt freier Karte
- Login nötig, weil echte Firmendaten. Keine Passwörter oder Schlüssel im Code oder im Repo (gehören in `.env`)
- Schreibweise Schweiz: "Strassenbau" mit ss
- Kleine Schritte: nach jeder fertigen Funktion ein Commit mit klarer Nachricht auf Deutsch
- Vor größeren Änderungen erst einen Plan zeigen

## Befehle
- Starten: `public/index.html` im Browser öffnen
- Veröffentlichung: Netlify veröffentlicht nur den Ordner `public` (siehe `netlify.toml`). Nur Dateien, die jeder sehen darf, gehören dort hinein. `CLAUDE.md`, Anleitungen und `.claude` bleiben ausserhalb.

## Aufgaben für später
- Gemeinsamer Datenspeicher mit Echtzeit, damit alle Handys denselben Stand sehen (z. B. Supabase, noch zu entscheiden)
- Push-Nachrichten aufs Handy bei Störung (Ton im Browser geht nicht bei gesperrtem Handy)
- Seite online stellen, automatisch aus GitHub
- Echte Datenquelle anbinden (Maschinendaten, Baustellenliste)
- Material-Daten der Baustellen aus echter Quelle
- Kartenanbieter für den Firmenbetrieb festlegen (Bedingungen von OpenFreeMap prüfen, Alternativen: swisstopo oder bezahlter Anbieter) und Adressen in Koordinaten umwandeln
- Optional: 3D-Gebäude und feineres Gelände, nur wenn es auf Handys flüssig bleibt
- Verlauf der Störungen und Auswertung
- Anmeldung und Rollen (Bauführer, Disponent, Chef)
