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
3. Damit die Maschine in der Szene und in 3D nicht nur als allgemeine Maschine erscheint: in `machKind` die Art erkennen, in `machShape` die Silhouette (SVG) ergänzen und in `MODELS3` das 3D-Modell, dazu `FOOT` und `TOPH` (Grösse für Ring und Schild) und bei Bedarf `MACH_SCALE`. Ohne diese Schritte wird die allgemeine Form `allg` gezeichnet.

**Demo-Daten:**
1. Suche in `public/index.html` die Funktion `loadDemo` und die Hilfsfunktion `M(...)`.
2. Füge eine Zeile hinzu: `M(id, name, typ, sparte, site, status)`. Es gibt keinen Tank-Wert mehr, nur die Meldung "Diesel fehlt".
   - `sparte`: `"garten"`, `"strasse"` oder `"tief"`
   - `site`: Id einer Demo-Baustelle oder `null` (Werkhof)
   - `status`: `"running"` auf einer Baustelle, sonst `"off"`

**Neues Feld an Maschinen (zum Beispiel Kennzeichen):**
1. `supabase/schema.sql`: Spalte bei `machines` ergänzen (mit `alter table ... add column if not exists`, damit bestehende Datenbanken funktionieren).
2. `public/index.html`: `mapMachine`, `dbMachine`, `createMachine` und das Formular `modalMachine` anpassen.
3. Zugriffsregeln prüfen und `tests/db_test.sh` sowie `tests/app_test.py` ergänzen.

Danach Tests laufen lassen, im Browser prüfen und mit einem Commit auf Deutsch speichern, zum Beispiel "Kennzeichen bei Maschinen ergänzt".
Status-Farben aus `CLAUDE.md` nicht ändern.
