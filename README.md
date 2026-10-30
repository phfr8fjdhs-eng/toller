# Baustellen-Dashboard

Ein Dashboard für eine Firma mit Gartenbau, Strassenbau und Tiefbau. Eine Karte von oben zeigt die Baustellen
mit ihren Maschinen. Jede Maschine hat einen Status, bei Störung gibt es Alarm.
Ohne Einrichtung läuft die Seite im **Demo-Modus** mit erfundenen Daten. Mit Supabase (siehe `SUPABASE-ANLEITUNG.md`) läuft sie im **Live-Modus**: Anmeldung, Freigabe durch einen Admin, gemeinsame Daten und Echtzeit auf allen Handys.

## Ausprobieren
Öffne `public/index.html` im Browser. Mit Internet erscheint eine **schlanke 3D-Karte von Rapperswil-Jona und Umgebung** (MapLibre, OpenFreeMap), ohne Internet eine Skizze.
Mit den Knöpfen links oben schaltest du 3D ein und aus oder gehst zurück zur Übersicht. Zwei Finger drehen und kippen die Karte.
Im Demo-Modus sind die Positionen der Baustellen Beispielwerte.
Eine Störung erscheint als rotes Banner und blinkende Maschine. Es gibt bewusst keinen Ton.

- Klick auf eine Baustelle: rechts siehst du ihre Maschinen
- Defekte Maschine: "Reparieren"
- Gelbe Maschine: "Tanken" oder "Nachliefern" (wenn Material fehlt)
- "Zurück" schickt eine Maschine in den Werkhof, "+ Maschine" holt sie aus dem Werkhof auf die gewählte Baustelle
- Oben filterst du nach Sparte
- Live-Modus: "+ Baustelle" (mit Adresssuche oder Kartenklick), "+ Maschine", Admins verwalten "Benutzer"

## Ordner
- `public/index.html`: die ganze Seite
- `public/config.js`: Einstellungen (Supabase-Adresse, anon-Key, Werkhof)
- `supabase/schema.sql`: Tabellen und Zugriffsregeln; `supabase/beispieldaten.sql`: optionale Beispieldaten
- `SUPABASE-ANLEITUNG.md`: Datenbank einrichten
- `tests/`: automatische Tests (`bash tests/db_test.sh`, `python3 tests/app_test.py`)
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
