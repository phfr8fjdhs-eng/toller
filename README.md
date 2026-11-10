# Baustellen-Dashboard

Ein Dashboard für eine Firma mit Gartenbau, Strassenbau und Tiefbau. Eine Karte von oben zeigt die Baustellen
mit ihren Maschinen. Jede Maschine hat einen Status, bei Störung gibt es Alarm. Auf jeder Baustelle steht frei geschrieben, was gebraucht wird (Bedarf).
Ohne Einrichtung läuft die Seite im **Demo-Modus** mit erfundenen Daten. Mit Supabase (siehe `SUPABASE-ANLEITUNG.md`) läuft sie im **Live-Modus**: Anmeldung, Freigabe durch einen Admin, gemeinsame Daten und Echtzeit auf allen Handys.

## Ausprobieren
Öffne `public/index.html` im Browser. Mit Internet erscheint im Modus 3D eine **schlanke 3D-Karte von Rapperswil-Jona und Umgebung** (MapLibre, OpenFreeMap), ohne Internet oder im Modus Leicht eine Skizze.
Mit den Knöpfen links oben auf der Karte schaltest du das Gelände 3D ein und aus oder gehst zurück zur Übersicht. Zwei Finger drehen und kippen die Karte.

**Zwei Modi** (Knopf "Modus" oben): **Leicht** ist für ältere Handys, ohne Karte und ohne 3D, spart Arbeitsspeicher und Daten.
**3D** ist für Computer, mit Karte und der **3D-Ansicht einer Baustelle** (Knopf "3D-Ansicht": jede Maschine in 3D, die Baustelle passt zu Sparte und Maschinen, mit Bedarfstafel). Beim ersten Öffnen wählt die Seite nach Gerät, die Wahl wird gemerkt.
Im Demo-Modus sind die Positionen der Baustellen Beispielwerte.
Eine Störung erscheint als rotes Banner und blinkende Maschine. Es gibt bewusst keinen Ton.

- Klick auf eine Baustelle: rechts siehst du ihre Maschinen
- Bedarf: Auf der Baustelle frei schreiben, was gebraucht wird, abhaken wenn erledigt (alle Freigegebenen). Es gibt bewusst keine Prozentanzeigen für Material
- Läuft eine Maschine nicht: "Defekt", "Material fehlt" oder "Diesel fehlt" melden. Danach "Repariert", "Nachgeliefert" oder "Getankt". An der Maschine steht, wer es gemeldet hat und wann
- "Material fehlt" öffnet eine Auswahl mit über 450 Materialien (suchen, nach Kategorie filtern). Fehlt etwas in der Liste, tippst du den Namen ein und wählst "neu hinzufügen", das darf jede freigegebene Person und danach steht es allen zur Verfügung. Dazu freiwillig Menge oder Hinweis
- "Werkhof" schickt eine Maschine in den Werkhof zurück, bei "Aus dem Werkhof einsetzen" holst du sie auf die gewählte Baustelle
- Oben filterst du nach Sparte, mehrere gleichzeitig sind möglich (zum Beispiel Gartenbau und Strassenbau)
- Live-Modus: "+ Baustelle" (mit Adresssuche oder Kartenklick), "+ Maschine", Admins verwalten "Benutzer"
- "Wartung" an jeder Maschine: Betriebsstunden, Service-Intervall und Termin von Hand eintragen. Ist der Service fällig, steht es als Text an der Maschine, als Chip "Service fällig" oben und als ruhiger Hinweis (kein Blinken, kein Ton). "Service erledigt" setzt den Zähler zurück
- "Verlauf": zeigt, welche Maschine wie oft und wie lange gestört war oder auf Material oder Diesel gewartet hat. Die Datenbank schreibt mit, niemand kann es von Hand ändern
- Passwort vergessen: Im Login auf "Passwort vergessen?" tippen, E-Mail eingeben, Link in der Mail öffnen, neues Passwort setzen
- Admin: Im Fenster "Neue Baustelle" kannst du den Text einer Offerte oder Beschreibung einfügen. Du bekommst einen Vorschlag für Name, Sparte, Ort auf der Karte und Bedarf. Du prüfst und speicherst. Preise werden nicht übernommen und der Text wird nicht gespeichert (PDF: Text kopieren)

## Ordner
- `public/index.html`: die ganze Seite
- `public/config.js`: Einstellungen (Supabase-Adresse, anon-Key, Werkhof)
- `public/materialien.js`: Materialkatalog für "Material fehlt" (Vorschlagsliste, bitte an die Firma anpassen)
- `supabase/schema.sql`: Tabellen und Zugriffsregeln; `supabase/beispieldaten.sql`: optionale Beispieldaten
- `SUPABASE-ANLEITUNG.md`: Datenbank einrichten
- `tests/`: automatische Tests (`bash tests/db_test.sh`, `python3 tests/app_test.py`, `python3 tests/speicher_test.py`). Das echte 3D-Bild prüfen sie nicht, das muss man einmal selbst ansehen
- `GITHUB-ANLEITUNG.md`: was du bei GitHub machst, was Claude Code macht, und wie die Seite für mehrere Handys online geht
- `CLAUDE.md`: das Gedächtnis des Projekts, Claude Code liest es bei jedem Start
- `.claude/agents/tester.md`: Spezialist, der Änderungen prüft
- `.claude/skills/neue-maschine/`: Anleitung zum Einbauen neuer Maschinen
- `.claude/skills/neue-baustelle/`: Anleitung zum Einbauen neuer Baustellen

---

# GitHub-Anleitung (Schritt für Schritt)

## Begriffe
- **Repository (Repo):** dein Projektordner, den Git verwaltet
- **Commit:** ein gespeicherter Stand mit Beschreibung
- **Branch:** eine Arbeitskopie zum Ausprobieren
- **Push:** Commits zu GitHub hochladen
- **Pull Request (PR):** Änderungen prüfen, bevor sie ins Hauptprojekt kommen

## 1. Einmalig einrichten
1. Konto auf github.com erstellen
2. Git installieren (git-scm.com) und im Terminal setzen:
   ```
   git config --global user.name "Dein Name"
   git config --global user.email "deine@mail.ch"
   ```

## 2. Repo erstellen
Wichtig: Wenn die Firma echte Daten nutzt, das Repo auf GitHub **privat** anlegen.

1. Auf GitHub: **New repository**, Name `baustellen-dashboard`, **Private**, ohne README
2. Im Terminal im Projektordner:
   ```
   git init
   git add .
   git commit -m "Erster Stand: Prototyp des Baustellen-Dashboards"
   git branch -M main
   git remote add origin https://github.com/DEIN-NAME/baustellen-dashboard.git
   git push -u origin main
   ```

## 3. Täglicher Ablauf
```
git checkout -b neue-funktion      # neuer Branch
claude                              # Claude Code starten, Plan-Modus nutzen
git add .
git commit -m "Beschreibung auf Deutsch"
git push -u origin neue-funktion
```
Dann auf GitHub einen **Pull Request** öffnen, Änderungen ansehen und mit **Merge** übernehmen.

## 4. Claude Code richtig nutzen
- Mit `claude` im Projektordner starten
- Bei größeren Aufgaben zuerst den **Plan-Modus** nutzen (Umschalt+Tab), Plan prüfen, dann bauen lassen
- Kleine Schritte, nach jedem fertigen Schritt ein Commit
- Wichtige Regeln immer in `CLAUDE.md` ergänzen
- Den Tester-Agent nach größeren Änderungen einsetzen
- Wiederkehrende Abläufe als Skill unter `.claude/skills/` speichern

## 5. Wenn etwas schiefgeht
- Änderungen ansehen: `git status` und `git diff`
- Nicht gespeicherte Änderungen verwerfen: `git restore .`
- Zu einem früheren Stand schauen: `git log --oneline`

## 6. Echte Firmendaten
- Keine Passwörter, Zugangsschlüssel oder Kundendaten in den Code oder ins Repo schreiben
- Solche Werte gehören in eine Datei `.env`, die in `.gitignore` steht
