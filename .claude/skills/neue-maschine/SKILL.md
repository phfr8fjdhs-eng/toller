---
name: neue-maschine
description: Anleitung, um eine neue Maschine ins Baustellen-Dashboard einzubauen. Verwenden, wenn der Nutzer eine Maschine hinzufügen will.
---

# Neue Maschine einbauen

Im Live-Modus legen Mitarbeiter Maschinen selbst in der Seite an (Knopf "+ Maschine"). Dafür ist kein Code nötig.

## Nur wenn der Nutzer Code ändern will

**Neue Maschinenart (Vorschlagsliste):**
1. Öffne `public/index.html` und suche `TYPEN`.
2. Füge die Art als Text hinzu, zum Beispiel `"Kehrmaschine"`.

**Demo-Daten:**
1. Suche in `public/index.html` die Funktion `loadDemo` und die Hilfsfunktion `M(...)`.
2. Füge eine Zeile hinzu: `M(id, name, typ, sparte, site, status, tank)`.
   - `sparte`: `"garten"`, `"strasse"` oder `"tief"`
   - `site`: Id einer Demo-Baustelle oder `null` (Werkhof)
   - `status`: `"running"` auf einer Baustelle, sonst `"off"`

**Neues Feld an Maschinen (zum Beispiel Kennzeichen):**
1. `supabase/schema.sql`: Spalte bei `machines` ergänzen (mit `alter table ... add column if not exists`, damit bestehende Datenbanken funktionieren).
2. `public/index.html`: `mapMachine`, `dbMachine`, `createMachine` und das Formular `modalMachine` anpassen.
3. Zugriffsregeln prüfen und `tests/db_test.sh` sowie `tests/app_test.py` ergänzen.

Danach Tests laufen lassen, im Browser prüfen und mit einem Commit auf Deutsch speichern, zum Beispiel "Kennzeichen bei Maschinen ergänzt".
Status-Farben aus `CLAUDE.md` nicht ändern.
