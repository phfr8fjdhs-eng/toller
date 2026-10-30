# GitHub-Anleitung: Was du machst und was Claude macht

## Kurz gesagt
Nicht alles kann Claude für dich erledigen. **Konto, Anmeldung und Freigaben musst du selbst machen.**
Danach kann **Claude Code auf deinem Computer** die Git-Arbeit übernehmen (Commits, Branches, Pull Requests).
In diesem Chat habe ich keinen Zugriff auf dein GitHub-Konto.

## Wer macht was

| Aufgabe | Du | Claude Code |
|---|---|---|
| GitHub-Konto erstellen, Zwei-Faktor-Schutz einschalten | ja | nein |
| Git installieren | ja | nein |
| Bei GitHub anmelden (`gh auth login`) | ja | nein |
| Repository erstellen | im Browser oder mit einem Befehl | ja, nach deiner Anmeldung |
| Änderungen speichern (Commit) | nein | ja |
| Branch anlegen | nein | ja |
| Hochladen (Push) | nein | ja, nach deiner Anmeldung |
| Pull Request öffnen | nein | ja, mit `gh` |
| Pull Request prüfen und übernehmen (Merge) | ja, du entscheidest | nein |
| Mitarbeiter einladen, Rechte vergeben | ja | nein |
| Passwörter und Schlüssel verwalten | ja | nie in Chat oder Code schreiben |

## Schritt 1: Konto (einmalig, du)
1. Auf github.com ein Konto erstellen.
2. Zwei-Faktor-Schutz einschalten (Settings, Password and authentication).
3. Gehört das Projekt der Firma, lege besser eine **Organisation** an (Profilbild, "Your organizations", "New organization"). Dann gehört der Code der Firma und nicht deinem privaten Konto.

## Schritt 2: Programme installieren (einmalig, du)
1. **Git:** git-scm.com
2. **GitHub CLI (`gh`):** cli.github.com
3. Im Terminal deinen Namen setzen:
   ```
   git config --global user.name "Dein Name"
   git config --global user.email "deine@mail.ch"
   ```
4. Anmelden:
   ```
   gh auth login
   ```
   Wähle GitHub.com, HTTPS und die Anmeldung im Browser. Ab jetzt darf Claude Code in deinem Namen arbeiten.

## Schritt 3: Repository erstellen (einmalig)
Wichtig: **privat** anlegen, weil es um echte Firmendaten geht.

**Variante A, im Browser:**
1. github.com, oben rechts "+", "New repository"
2. Name `baustellen-dashboard`, **Private**, ohne README
3. Im Projektordner:
   ```
   git init
   git add .
   git commit -m "Erster Stand: Prototyp des Baustellen-Dashboards"
   git branch -M main
   git remote add origin https://github.com/DEIN-NAME/baustellen-dashboard.git
   git push -u origin main
   ```

**Variante B, mit einem Befehl (nach `gh auth login`):**
```
git init
git add .
git commit -m "Erster Stand: Prototyp des Baustellen-Dashboards"
gh repo create baustellen-dashboard --private --source=. --remote=origin --push
```

## Schritt 4: Mit Claude Code arbeiten (immer wieder)
1. Im Projektordner `claude` starten.
2. Gib eine Aufgabe, zum Beispiel:
   "Lege einen neuen Branch an, baue die Sparten-Filter für das Handy, committe in kleinen Schritten und öffne einen Pull Request."
3. Bei grösseren Aufgaben zuerst den Plan-Modus nutzen (Umschalt+Tab) und den Plan prüfen.
4. Nach grösseren Änderungen den Tester-Agent einsetzen lassen.

## Schritt 5: Prüfen und übernehmen (du)
1. Auf GitHub den Pull Request öffnen.
2. Unter "Files changed" ansehen, was geändert wurde.
3. Passt alles: "Merge pull request". Sonst eine Rückmeldung schreiben oder Claude Code nachbessern lassen.

## Schritt 6: Schutz (empfohlen, du)
- In den Repo-Einstellungen eine Regel für den Branch `main` anlegen, damit Änderungen nur über Pull Requests hineinkommen.
- Nur Personen einladen, die wirklich Zugriff brauchen.

---

# Mehrere Handys gleichzeitig

## Das Problem
Der Prototyp läuft nur auf einem Gerät. Jedes Handy würde seine **eigene** Simulation sehen.
Damit alle Handys **denselben Stand** sehen (wenn der Bauführer eine Maschine meldet, sieht es das Büro sofort), braucht es einen gemeinsamen Datenspeicher im Internet.

## Der Aufbau
```
Handys (Browser)  <-->  Online-Dienst (Datenbank + Echtzeit + Login)
        ^
        |  Seite wird online bereitgestellt, automatisch aus GitHub
```

## Was du brauchst
1. **Datenbank mit Echtzeit und Login.** Vorschlag: **Supabase** (Datenbank, Echtzeit-Updates und Anmeldung in einem). Eine Alternative ist Firebase.
2. **Hosting für die Webseite**, das sich mit GitHub verbindet (zum Beispiel Cloudflare Pages oder Netlify). Dann ist die Seite nach jedem Merge automatisch aktualisiert.
3. **Login** für Mitarbeiter, damit nicht jeder die Firmendaten sieht.

Wichtig: Prüfe vor der Wahl die Preise und Nutzungsbedingungen. Manche Gratis-Stufen gelten nur für private Nutzung und nicht für Firmen.

## Wer macht was
- **Du:** Konten bei Datenbank-Dienst und Hosting anlegen, die Dienste mit GitHub verbinden, Zugangsschlüssel sicher aufbewahren.
- **Claude Code:** Tabellen entwerfen, den Code für Echtzeit-Sync und Login schreiben, die Seite für das Handy verbessern, alles in Pull Requests liefern.
- Schlüssel kommen in eine Datei `.env`, die nicht ins Repo gehört (steht in `.gitignore`). Nie in den Chat oder in den Code kopieren.

## Besonderheiten bei Handys
- **Alarm:** Die Seite zeigt Störungen nur, solange sie offen ist (Banner und blinkende Maschine, ohne Ton). Bei gesperrtem Bildschirm kommt nichts an. Dafür braucht es **Push-Nachrichten**. Auf dem iPhone funktioniert das nur, wenn die Seite zum Home-Bildschirm hinzugefügt wurde.
- **Bedienung:** Grosse Buttons, Liste statt freier Karte auf kleinen Bildschirmen (im Prototyp schon eingebaut).
- **Rechte:** Entscheide, wer nur ansehen und wer Status ändern darf (zum Beispiel Bauführer, Disponent, Chef). Sonst kann jeder alles verändern.
- **Gleichzeitige Änderungen:** Wenn zwei Personen dieselbe Maschine ändern, gilt der letzte Stand. Das sollte vorher festgelegt werden.

## Echte Karte
- Die Seite zeigt eine schlanke 3D-Karte mit MapLibre. Den Kartenstil liefert OpenFreeMap (ohne Schlüssel), die Höhendaten kommen von AWS Terrain Tiles. Dafür braucht sie Internet, sonst erscheint die Skizze. Im Modus Leicht (für ältere Handys) gibt es keine Karte, nur die Skizze, und three.js und MapLibre werden gar nicht erst geladen.
- Die Karte ist absichtlich einfach gehalten (kein 3D-Gebäude-Modell), damit sie auf Handys flüssig läuft. Mit dem Knopf "3D" schaltest du auf eine flache Ansicht.
- Prüfe vor dem Firmenbetrieb die Nutzungsbedingungen von OpenFreeMap (openfreemap.org/tos). Alternativen sind swisstopo (für die Schweiz) oder ein bezahlter Kartenanbieter.
- Baustellen legst du in der Seite an (Adresssuche, Kartenklick oder Koordinaten). Die Positionen stehen in der Datenbank (`lat`, `lng`).

## Reihenfolge (Vorschlag)
1. GitHub einrichten und Repo hochladen (Schritte 1 bis 3 oben)
2. Seite online stellen (zuerst im Demo-Modus)
3. Supabase einrichten (Datenbank, Login, Echtzeit): siehe `SUPABASE-ANLEITUNG.md`
4. Echte Baustellen und Maschinen eintragen
5. Push-Nachrichten für Störungen
