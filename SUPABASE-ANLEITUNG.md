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
   Solange das nicht gemacht ist, läuft die Seite weiter und zeigt beim Bedarf den Hinweis "Datenbank-Update nötig".
4. Optional: Dasselbe mit `supabase/beispieldaten.sql`, wenn du Beispielbaustellen zum Ausprobieren willst.

## 3. Anmeldung einstellen
1. **Authentication**, dann **URL Configuration**:
   - **Site URL:** die Adresse deiner Netlify-Seite (zum Beispiel `https://bespoke-sprite-674b0f.netlify.app`).
     Ohne das zeigen die Bestätigungs-Mails auf eine falsche Adresse.
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
| Baustellen und Maschinen löschen | nein | nein | ja |
| Benutzer freigeben und sperren | nein | nein | ja |

## Grenzen und Hinweise
- Eine Abfrage liefert höchstens 1000 Zeilen. Für deutlich mehr Baustellen oder Maschinen muss die Seite angepasst werden.
- Prüfe vor dem Betrieb die Preise und Bedingungen von Supabase. Soweit ich weiss, pausieren Gratis-Projekte bei längerer Inaktivität,
  und Datensicherungen gibt es meist erst in bezahlten Plänen. Für den echten Firmenbetrieb ist ein bezahlter Plan sinnvoll.
- Datenschutz: Die Daten liegen in der gewählten Region bei Supabase. Kläre das intern ab, bevor echte Daten hineinkommen.
- Passwort vergessen: Aktuell gibt es dafür noch keinen Knopf in der Seite. Ein Admin kann in Supabase unter
  **Authentication, Users** ein neues Passwort setzen.
- Excel-Anbindung ist noch nicht gebaut. Sie kommt später als eigener Schritt (siehe `CLAUDE.md`).

## Wenn etwas nicht klappt
- **"Warten auf Freigabe", obwohl du die erste Person bist:** Das Schema wurde vermutlich nicht ausgeführt, oder jemand hat sich vor dir registriert.
  Prüfe in Supabase unter **Table Editor, profiles**.
- **"permission denied" oder leere Listen:** Du bist noch nicht freigegeben, oder `schema.sql` fehlt.
- **Kein "live" oben, Änderungen erscheinen erst nach Neuladen:** Echtzeit ist nicht aktiv. Führe `schema.sql` noch einmal aus
  und prüfe unter **Database, Publications**, ob `sites`, `machines`, `needs` und `activity` bei `supabase_realtime` aufgelistet sind.
- **Bestätigungs-Mail kommt nicht:** Spam-Ordner prüfen, Site URL prüfen, oder die Person unter **Authentication, Users** selbst anlegen.
