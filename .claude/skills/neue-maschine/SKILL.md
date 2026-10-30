---
name: neue-maschine
description: Anleitung, um eine neue Maschine ins Baustellen-Dashboard einzubauen. Verwenden, wenn der Nutzer eine Maschine hinzufügen will.
---

# Neue Maschine einbauen

1. Öffne `index.html` und suche die Liste `machines`.
2. Füge einen neuen Eintrag hinzu:
   - `id`: nächste freie Nummer
   - `name`: kurzer, klarer Name (z. B. "Bagger 3")
   - `typ`: Art der Maschine (Bagger, Walze, Fertiger, Dumper, LKW, Radlader ...)
   - `sparte`: `"garten"`, `"strasse"` oder `"tief"`
   - `site`: Id einer Baustelle oder `null` (dann steht sie im Werkhof)
   - `status`: `"running"` wenn auf einer Baustelle, sonst `"off"`
   - `tank`: Zahl von 0 bis 100
   - `reason`: leer lassen (`""`)
3. Halte dich an die Status-Farben aus CLAUDE.md und ändere keine Farben.
4. Öffne die Seite: Die Maschine muss auf der richtigen Baustelle (oder im Werkhof) erscheinen und auf Klick reagieren.
5. Mache einen Commit auf Deutsch, z. B. "Maschine Bagger 3 hinzugefügt".
