---
name: neue-baustelle
description: Anleitung, um eine neue Baustelle ins Baustellen-Dashboard einzubauen. Verwenden, wenn der Nutzer eine Baustelle hinzufügen will.
---

# Neue Baustelle einbauen

Im Live-Modus legen Mitarbeiter Baustellen selbst in der Seite an (Knopf "+ Baustelle"): Name, Sparte, Ort per Adresssuche,
Kartenklick oder Koordinaten. Was gebraucht wird, schreiben sie danach frei als Bedarf auf die Baustelle. Dafür ist kein Code nötig.

## Nur wenn der Nutzer Code ändern will

**Demo-Daten:**
1. Suche in `public/index.html` die Funktion `loadDemo` und die Liste `sites`.
2. Füge einen Eintrag hinzu mit `id`, `name`, `sparte`, `x`, `y` (Prozent auf der Skizze) und `lat`, `lng` (echte Position). Es gibt keine Material-Prozente.
3. Offener Bedarf für die Demo: in `loadDemo` die Liste `needs` mit `N(id, baustellenId, text, stundenAlt)` ergänzen.
4. Prüfe, dass sich Marker auf der Skizze nicht überlappen und dass die Szene (Boden nach Sparte) und die 3D-Ansicht sinnvoll aussehen.

**Beispieldaten in der Datenbank:** `supabase/beispieldaten.sql` ergänzen (alle Namen erfunden, keine Material- oder Tank-Spalten).

**Werkhof verschieben:** `depot` in `public/config.js` ändern.

Danach Tests laufen lassen, im Browser prüfen und mit einem Commit auf Deutsch speichern, zum Beispiel "Beispielbaustelle Kreisel Ost ergänzt".
