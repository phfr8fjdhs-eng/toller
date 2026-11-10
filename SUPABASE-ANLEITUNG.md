# Supabase einrichten (Datenbank, Login, Echtzeit)

Supabase liefert die gemeinsame Datenbank, die Anmeldung und die Echtzeit-Updates. Du brauchst dafür etwa 15 Minuten.
Solange du das nicht gemacht hast, läuft die Seite im **Demo-Modus** mit erfundenen Daten.

> Wichtig: Der erste Test mit einer echten Supabase-Datenbank steht noch aus. Das Schema und die Zugriffsregeln
> wurden auf einer lokalen PostgreSQL getestet, die Seite gegen einen Ersatz. Plane den ersten Durchgang
> deshalb gemeinsam mit Claude und schicke Fehlermeldungen oder Screenshots.

## 1. Projekt anlegen
1. Auf **supabase.com** auf "Start your project" und mit GitHub anmelden.
2. **New project**. Name zum Beispiel `baustellen`.
3. **Database password:** Ein langes, neues Passwort wählen und im Passwort-Manager speichern. Niemandem schicken, auch Claude nicht.
4. **Region:** Eine Region in Europa, wenn möglich Zürich (`eu-central-2`), sonst Frankfurt.
5. **Create new project** und etwa zwei Minuten warten.

## 2. Datenbank einrichten
1. Links auf **SQL Editor**, dann **New query**.
2. Auf GitHub die Datei `supabase/schema.sql` öffnen, alles kopieren (Knopf "Copy raw file"), in Supabase einfügen und auf **Run** klicken.
3. Es sollte "Success" erscheinen. Das Schema lässt sich gefahrlos ein zweites Mal ausführen.
   **Update einer schon eingerichteten Datenbank** (zum Beispiel für den neuen Bedarf auf den Baustellen): `schema.sql` einfach noch einmal ausführen. Bestehende Daten bleiben erhalten.
   Nötig auch für die weiteren Sparten einer Baustelle, für das Zeichnen auf der Karte (neue Tabelle `drawings`) und für "Strasse erneuern, nur eine Seite" (Spalte `seite`).
   Solange das nicht gemacht ist, läuft die Seite weiter und zeigt beim Bedarf den Hinweis "Datenbank-Update nötig". Bei "Material fehlt" gehen Katalog und Meldung trotzdem, nur eigene Materialien werden noch nicht für alle gespeichert und der Absender einer Meldung fehlt.
   Wer eine Meldung abgeschickt hat, trägt die Datenbank selbst ein (Name aus dem Profil). Das lässt sich von der Seite aus nicht fälschen.
4. Optional: Dasselbe mit `supabase/beispieldaten.sql`, wenn du Beispielbaustellen zum Ausprobieren willst.

## 3. Anmeldung einstellen
1. **Authentication**, dann **URL Configuration**:
   - **Site URL:** die Adresse deiner Netlify-Seite (zum Beispiel `https://bespoke-sprite-674b0f.netlify.app`).
     Ohne das zeigen die Bestätigungs-Mails auf eine falsche Adresse.
   - **Redirect URLs:** dieselbe Adresse noch einmal eintragen (mit `/**` am Ende, zum Beispiel `https://bespoke-sprite-674b0f.netlify.app/**`).
     Der Link in der Mail "Passwort vergessen" führt sonst nicht zurück auf die Seite.
2. **Authentication**, dann **Sign In / Providers**, dann **Email**: "Confirm email" eingeschaltet lassen.
3. Hinweis: Der Mail-Versand von Supabase ist im Standard stark begrenzt. Wenn viele Mitarbeiter sich gleichzeitig registrieren,
   braucht es später einen eigenen Mail-Server (SMTP). Alternativ legst du Personen unter **Authentication, Users, Add user** selbst an.

## 4. Zwei Werte holen
1. **Project Settings** (Zahnrad), dann **API** (oder **API Keys**).
2. Kopiere:
   - **Project URL** (sieht aus wie `https://abcdefgh.supabase.co`)
   - den **anon** bzw. **publishable** Key
3. **Nie** den `service_role`- oder `secret`-Key weitergeben oder in die Seite schreiben. Er gibt Zugriff auf alle Daten.
   Der anon-Key ist für Browser gedacht. Geschützt sind die Daten durch die Zugriffsregeln aus `schema.sql`.

## 5. In die Seite eintragen
Schicke die beiden Werte an Claude, oder trage sie selbst in `public/config.js` ein:

```js
window.APP_CONFIG = {
  supabaseUrl: "https://abcdefgh.supabase.co",
  supabaseKey: "dein-anon-key",
  depot: { lat: 47.2340, lng: 8.8600 }   // Standort des Werkhofs
};
```
Nach dem Hochladen nach GitHub aktualisiert Netlify die Seite in etwa einer Minute.

## 6. Erste Anmeldung: du wirst Admin
**Mach das, bevor du den Link weitergibst.** Die allererste Person, die sich registriert, wird automatisch Admin.
1. Seite öffnen, "Neu hier? Konto anlegen", Name, E-Mail und Passwort (mindestens 8 Zeichen).
2. Bestätigungs-Mail öffnen und den Link anklicken, dann anmelden.
3. Oben erscheint der Knopf **Benutzer**.

## 7. Mitarbeiter einladen
1. Mitarbeiter öffnen die Seite und legen selbst ein Konto an.
2. Sie sehen zuerst nur "Warten auf Freigabe".
3. Du öffnest **Benutzer** und klickst bei der Person auf **Freigeben**. Sie klickt "Neu prüfen".
4. Wer einen Admin-Knopf braucht, bekommt **Zu Admin**.

## Fotos zu Meldungen einrichten
Zu einer offenen Meldung (Defekt, Material oder Diesel fehlt) lässt sich ein Foto hinzufügen. Die Bilder liegen im privaten Speicher
**meldungsfotos** (Supabase Storage). `schema.sql` richtet ihn beim Ausführen selbst ein: privat, nur JPEG, höchstens 1,5 MB, nur freigegebene Personen
lesen, laden hoch und löschen. Die Seite verkleinert jedes Bild vor dem Hochladen auf höchstens 1280 Pixel und entfernt dabei Ortsdaten und
andere Metadaten des Fotos.

So prüfst du es nach dem Ausführen von `schema.sql`:
1. In Supabase links **Storage** öffnen. Es muss ein Bucket **meldungsfotos** mit dem Hinweis "Private" da sein.
2. Fehlt er (die Meldung "Fotos zu Meldungen konnten nicht eingerichtet werden" erscheint dann unter den Ergebnissen des SQL Editors), lege ihn von Hand an:
   **New bucket**, Name `meldungsfotos`, **Public bucket aus**, **Restrict file size** 1.5 MB, **Allowed MIME types** `image/jpeg`.
   Danach `schema.sql` noch einmal ausführen, das ergänzt die Zugriffsregeln.
3. In der Seite bei einer defekten Maschine auf **Foto** tippen. Klappt es nicht, steht die Ursache in der roten Meldung.

Wichtig zu wissen:
- Ein Foto gehört nur zur offenen Meldung. Wird sie erledigt oder wechselt sie, löscht die Datenbank den Pfad und die Seite löscht die Datei. Wird die Meldung von
  einem Gerät ohne Verbindung oder von Hand in der Datenbank erledigt, kann eine Datei übrig bleiben. Sie ist unsichtbar und harmlos, nimmt aber Platz.
  Unter **Storage, meldungsfotos** lassen sich solche Dateien von Hand löschen (nicht per SQL löschen: dabei bleibt die eigentliche Datei bestehen).
- Auf Fotos können zufällig Personen zu sehen sein. Mitarbeiter darüber informieren und Fotos nur von Maschinen und Schäden machen.
- Die Anzeigeadressen der Fotos sind eine Stunde gültig und nur für angemeldete, freigegebene Personen erzeugbar.

## Alte Spalten entfernen (freiwillig)
Frühere Versionen hatten Prozent-Spalten für Material und Tank. Die Seite braucht sie nicht mehr. Sie stören nicht und können bleiben.
Wenn du aufräumen willst, im SQL Editor (löscht die Werte in diesen Spalten endgültig):
```sql
alter table public.sites drop column if exists material_name, drop column if exists material_level;
alter table public.machines drop column if exists tank;
```

## Wer darf was?
| | Nicht freigegeben | Mitarbeiter | Admin |
|---|---|---|---|
| Daten sehen | nein | ja | ja |
| Baustellen und Maschinen anlegen | nein | ja | ja |
| Status ändern, Material oder Diesel fehlt melden | nein | ja | ja |
| Bedarf auf einer Baustelle schreiben und abhaken | nein | ja | ja |
| Bedarf löschen | nein | nur eigener | ja |
| Eigenes Material in der Auswahl ergänzen | nein | ja | ja |
| Eigenes Material löschen | nein | nur eigenes | ja |
| Sehen, wer eine Meldung abgeschickt hat | nein | ja | ja |
| Foto zu einer Meldung hinzufügen, ansehen, ersetzen, entfernen | nein | ja | ja |
| Wartung (Betriebsstunden, Service) eintragen | nein | ja | ja |
| Verlauf der Störungen ansehen | nein | ja | ja |
| Verlauf ändern oder löschen | nein | nein | nein (nur die Datenbank schreibt ihn) |
| Baustellen und Maschinen löschen | nein | nein | ja |
| Benutzer freigeben und sperren | nein | nein | ja |

## Grenzen und Hinweise
- Eine Abfrage liefert höchstens 1000 Zeilen. Für deutlich mehr Baustellen oder Maschinen muss die Seite angepasst werden.
- Prüfe vor dem Betrieb die Preise und Bedingungen von Supabase. Soweit ich weiss, pausieren Gratis-Projekte bei längerer Inaktivität,
  und Datensicherungen gibt es meist erst in bezahlten Plänen. Für den echten Firmenbetrieb ist ein bezahlter Plan sinnvoll.
- Datenschutz: Die Daten liegen in der gewählten Region bei Supabase. Kläre das intern ab, bevor echte Daten hineinkommen.
- Passwort vergessen: Aktuell gibt es dafür noch keinen Knopf in der Seite. Ein Admin kann in Supabase unter
  **Authentication, Users** ein neues Passwort setzen.
- Neue Funktionen (Wartung, Fotos) brauchen ein erneutes Ausführen von `schema.sql`. Bis dahin läuft die Seite weiter, zeigt aber diese Funktionen nicht oder mit einem Hinweis.
- Excel-Anbindung ist noch nicht gebaut. Sie kommt später als eigener Schritt (siehe `CLAUDE.md`).

## Wenn etwas nicht klappt
- **"Warten auf Freigabe", obwohl du die erste Person bist:** Das Schema wurde vermutlich nicht ausgeführt, oder jemand hat sich vor dir registriert.
  Prüfe in Supabase unter **Table Editor, profiles**.
- **"permission denied" oder leere Listen:** Du bist noch nicht freigegeben, oder `schema.sql` fehlt.
- **Kein "live" oben, Änderungen erscheinen erst nach Neuladen:** Echtzeit ist nicht aktiv. Führe `schema.sql` noch einmal aus
  und prüfe unter **Database, Publications**, ob `sites`, `machines`, `needs`, `materials` und `activity` bei `supabase_realtime` aufgelistet sind.
- **"Passwort vergessen": Link führt auf eine falsche Seite oder meldet "abgelaufen":** Site URL und Redirect URLs prüfen (Schritt 3). Der Link gilt nur einmal und etwa eine Stunde. Danach unter "Passwort vergessen?" einen neuen anfordern. Nach dem Klick auf den Link kommt zuerst "Neues Passwort", erst danach die Daten.
- **"Passwort vergessen": die Mail kommt nicht:** Spam-Ordner, und wie oben: Der Standard-Versand von Supabase ist stark begrenzt, für den Firmenbetrieb braucht es einen eigenen Mail-Server (SMTP). Die Seite antwortet absichtlich immer gleich, ob es die Adresse gibt oder nicht. Notlösung: unter **Authentication, Users** das Passwort der Person selbst setzen.
- **Bestätigungs-Mail kommt nicht:** Spam-Ordner prüfen, Site URL prüfen, oder die Person unter **Authentication, Users** selbst anlegen.
