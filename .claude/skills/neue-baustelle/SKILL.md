---
name: neue-baustelle
description: Anleitung, um eine neue Baustelle ins Baustellen-Dashboard einzubauen. Verwenden, wenn der Nutzer eine Baustelle hinzufügen will.
---

# Neue Baustelle einbauen

1. Öffne `public/index.html` und suche die Liste `sites`.
2. Füge einen neuen Eintrag hinzu:
   - `id`: neue, eindeutige Id (z. B. `"s6"`)
   - `name`: Name der Baustelle
   - `sparte`: `"garten"`, `"strasse"` oder `"tief"`
   - `material`: `{ name: "Kies", level: 100 }` mit dem wichtigsten Material
   - `x`, `y`: Position in Prozent auf der Skizze (0-100), nicht zu nah an einer anderen Baustelle
   - `lat`, `lng`: echte Koordinaten für die Karte (Breitengrad, Längengrad)
3. Weise Maschinen zu, indem du bei `machines` die Id bei `site` einträgst.
4. Prüfe, dass sich keine Marker überlappen und die Baustelle den schlechtesten Status ihrer Maschinen zeigt.
5. Mache einen Commit auf Deutsch, z. B. "Baustelle Kreisel Ost hinzugefügt".
