---
name: neue-baustelle
description: Anleitung, um eine neue Baustelle ins Baustellen-Dashboard einzubauen. Verwenden, wenn der Nutzer eine Baustelle hinzufügen will.
---

# Neue Baustelle einbauen

Im Live-Modus legen Mitarbeiter Baustellen selbst in der Seite an (Knopf "+ Baustelle"): Name, Sparte, Material, Ort per Adresssuche,
Kartenklick oder Koordinaten. Dafür ist kein Code nötig.

## Nur wenn der Nutzer Code ändern will

**Neues Material in der Vorschlagsliste:**
1. Öffne `public/index.html` und suche `MATERIALS`.
2. Füge das Material als Text hinzu.

**Demo-Daten:**
1. Suche in `public/index.html` die Funktion `loadDemo` und die Liste `sites`.
2. Füge einen Eintrag hinzu mit `id`, `name`, `sparte`, `material:{name, level}`, `x`, `y` (Prozent auf der Skizze) und `lat`, `lng` (echte Position).
3. Prüfe, dass sich Marker auf der Skizze nicht überlappen.

**Beispieldaten in der Datenbank:** `supabase/beispieldaten.sql` ergänzen (alle Namen erfunden).

**Werkhof verschieben:** `depot` in `public/config.js` ändern.

Danach Tests laufen lassen, im Browser prüfen und mit einem Commit auf Deutsch speichern, zum Beispiel "Beispielbaustelle Kreisel Ost ergänzt".
