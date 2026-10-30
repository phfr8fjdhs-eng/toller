// Materialkatalog: Vorschlagsliste für "Material fehlt" (Suche in der Seite).
// Übliche Bezeichnungen im Garten-, Strassen- und Tiefbau, nach Kategorie geordnet. Bitte an die Firma anpassen.
// Eigene Einträge, die Mitarbeiter in der Seite ergänzen, stehen zusätzlich in der Datenbank (Tabelle materials)
// und gelten für alle. Hier nur öffentliche, erfundene bzw. allgemeine Angaben, keine Firmendaten.
// Aufbau: [ ["Kategorie", ["Material", "Material", ...]], ... ]. Namen müssen innerhalb des Katalogs einmalig sein.
window.MATERIAL_KATALOG = [
  ["Kies, Sand, Splitt", [
    "Kies 0/16", "Kies 0/32", "Kies 0/45", "Kies 0/63", "Kiessand 0/32", "Frostschutzkies 0/45", "Planiekies", "Wandkies",
    "Rundkies 8/16", "Rundkies 16/32", "Rundkies 32/63", "Schotter 32/63", "Grobschotter 63/125",
    "Splitt 2/5", "Splitt 5/8", "Splitt 8/11", "Splitt 11/22", "Splitt 22/32", "Brechsand 0/4", "Brechsand 0/2", "Fugensand 0/2",
    "Sand 0/4 gewaschen", "Betonsand 0/4", "Mörtelsand 0/2", "Bettungssand", "Spielsand", "Rohrbettungskies 4/8", "Rohrumhüllungskies 0/16",
    "Drainagekies 8/16", "Filterkies 4/8", "Zierkies weiss", "Zierkies grau", "Ziersplitt", "Kalksplitt", "Mergel", "Hinterfüllmaterial",
    "Recyclingkies 0/45 (RC)", "RC-Kiessand", "Recyclingschotter"
  ]],
  ["Beton und Mörtel", [
    "Beton C20/25", "Beton C25/30", "Beton C30/37", "Beton C30/37 Frost-Tausalz", "Magerbeton", "Sauberkeitsschicht Beton", "Unterlagsbeton", "Fliessbeton",
    "Spritzbeton", "Sichtbeton", "Schnellbeton", "Estrich", "Zement im Sack 25 kg", "Zement lose", "Schnellzement",
    "Fertigmörtel", "Kalkzementmörtel", "Versetzmörtel", "Fugenmörtel", "Drainmörtel", "Haftbrücke", "Grundierung",
    "Betonzusatzmittel", "Verzögerer", "Nachbehandlungsmittel", "Trennmittel (Schalöl)"
  ]],
  ["Schalung und Armierung", [
    "Schalungsplatten", "Schaltafeln", "Schalungsträger", "Rundschalung", "Randschalung", "Abstandhalter", "Distanzhalter",
    "Armierungseisen Ø 8", "Armierungseisen Ø 10", "Armierungseisen Ø 12", "Armierungseisen Ø 14", "Armierungseisen Ø 16",
    "Armierungsmatten Q188", "Armierungsmatten Q257", "Armierungsmatten Q335", "Bewehrungskörbe", "Bindedraht", "Fugenband", "Dehnfugenplatten"
  ]],
  ["Asphalt und Belag", [
    "Asphalt AC 8 N (Deckschicht)", "Asphalt AC 11 N (Deckschicht)", "Asphalt AC B 22 (Binderschicht)", "Asphalt AC T 22 (Tragschicht)", "Asphalt AC T 32 (Tragschicht)",
    "Gussasphalt", "Splittmastixasphalt", "Offenporiger Asphalt", "Asphalt für Handeinbau", "Kaltasphalt im Sack", "Flickasphalt (Kaltmischgut)",
    "Fräsgut", "Recyclingasphalt", "Bitumenemulsion", "Anspritzemulsion", "Haftkleber", "Bitumen", "Bitumenanstrich", "Fugenvergussmasse", "Fugenband bituminös",
    "Abstreusplitt", "Markierfarbe weiss", "Markierfarbe gelb", "Thermoplast Markierung", "Glasperlen für Markierung", "Mergelbelag"
  ]],
  ["Randsteine, Pflaster, Platten, Mauern", [
    "Randstein Beton", "Randstein Granit", "Randstein Bordsteinabsenkung", "Rasenkantenstein", "Mähkante", "Stellriemen", "Winkelstein (L-Stein)",
    "Verbundstein", "Pflasterstein Beton", "Rasengittersteine", "Rasenfugenstein", "Granitpflaster", "Granitkleinpflaster", "Kopfsteinpflaster",
    "Betonplatten 40x40", "Betonplatten 50x50", "Gehwegplatten", "Terrassenplatten", "Natursteinplatten", "Feinsteinzeugplatten", "Taktile Bodenindikatoren",
    "Treppenstufen Beton", "Blockstufen Granit", "Granitpalisaden", "Betonpalisaden", "Holzpalisaden",
    "Mauerstein Naturstein", "Bruchstein", "Findling", "Quader", "Trockenmauersteine", "Mauerscheiben (L-Elemente)", "Betonmauerelemente",
    "Gabionenkörbe", "Gabionenfüllung", "Entwässerungsrinne", "Pflasterrinne"
  ]],
  ["Rohre, Schächte, Leitungen", [
    "KG-Rohr DN 125", "KG-Rohr DN 150", "KG-Rohr DN 200", "KG-Rohr DN 250", "KG-Rohr DN 300", "KG-Rohr DN 400", "KG-Bogen", "KG-Abzweiger", "KG-Muffe",
    "Steinzeugrohr", "Betonrohr DN 300", "Betonrohr DN 500", "Betonrohr DN 800", "Betonrohr DN 1000",
    "PE-Rohr 32", "PE-Rohr 63", "PE-Rohr 110", "PE-Rohr 160", "Gussrohr DN 100", "Gussrohr DN 150", "Formstücke", "Dichtungsring", "Gleitmittel für Rohre",
    "Kabelschutzrohr Ø 50", "Kabelschutzrohr Ø 100", "Kabelschutzrohr Ø 125", "Kabelschutzrohr Ø 160", "Leerrohr", "Einziehband", "Warnband", "Ortungsband",
    "Schachtring", "Schachtkonus", "Schachtunterteil", "Schachtdeckel", "Schachtabdeckung D400", "Steigeisen", "Strassenablauf", "Strassenrost", "Schlammsammler",
    "Hydrant", "Wasserschieber", "Rückstauklappe", "Verschlussstopfen", "Sickerrohr DN 100", "Drainagerohr gelocht", "Sickerschacht", "Versickerungsrigole"
  ]],
  ["Erde und Garten", [
    "Humus (Oberboden)", "Humus gesiebt", "Unterboden", "Pflanzerde", "Pflanzsubstrat", "Baumsubstrat", "Dachgartensubstrat", "Rasensubstrat", "Magerrasensubstrat",
    "Kompost", "Rindenmulch", "Rindenhumus", "Holzschnitzel", "Hackschnitzel", "Torffreie Erde",
    "Rasensamen Gebrauchsrasen", "Rasensamen Sportrasen", "Rasensamen Schattenrasen", "Blumenwiese Saatgut", "Rollrasen",
    "Rasendünger", "Langzeitdünger", "Hornspäne", "Gartenkalk", "Mulchfolie", "Unkrautvlies", "Wurzelschutzvlies",
    "Baumpfahl", "Baumbinder", "Ballenanker", "Stammschutz", "Gartenvlies"
  ]],
  ["Bäume", [
    "Spitzahorn", "Bergahorn", "Feldahorn", "Kugelahorn", "Birke", "Rotbuche", "Hainbuche", "Säulenhainbuche", "Stieleiche", "Linde", "Platane", "Esche",
    "Kirschbaum", "Zierkirsche", "Apfelbaum Hochstamm", "Birnbaum", "Zwetschgenbaum", "Nussbaum", "Rosskastanie", "Weide", "Magnolie", "Felsenbirne",
    "Tulpenbaum", "Ginkgo", "Waldföhre", "Fichte", "Tanne", "Eibe", "Lärche", "Eiche"
  ]],
  ["Sträucher, Hecken, Stauden", [
    "Kirschlorbeer", "Thuja", "Liguster", "Buchs", "Heckenpflanzen Hainbuche", "Heckenpflanzen Rotbuche", "Heckenpflanzen Feldahorn", "Forsythie", "Hortensie",
    "Flieder", "Schneeball", "Haselstrauch", "Hartriegel", "Weigelie", "Spierstrauch", "Berberitze", "Rosen", "Lavendel", "Rhododendron", "Beerensträucher", "Bambus",
    "Efeu", "Kletterhortensie", "Wilder Wein", "Clematis", "Bodendecker", "Stauden gemischt", "Ziergräser", "Farne", "Funkien", "Sonnenhut", "Storchschnabel",
    "Kräuter", "Sommerblumen", "Blumenzwiebeln", "Tulpenzwiebeln"
  ]],
  ["Garten und Aussenanlage", [
    "Tropfschlauch", "Versenkregner", "Bewässerungsrohr PE 25", "Bewässerungssteuerung", "Magnetventil", "Gartenschlauch", "Rasenkante Aluminium", "Rasenkante Stahl",
    "Terrassendielen Holz", "Terrassendielen WPC", "Lärchenholz", "Douglasienholz", "Eichenholz", "Holzbohlen", "Holzpfosten", "Staketen", "Zaunelemente",
    "Doppelstabmatten", "Maschendraht", "Zaunpfosten", "Hochbeetelemente", "Rankgitter", "Fallschutzkies", "Fallschutz Hackschnitzel"
  ]],
  ["Absperrung und Sicherheit", [
    "Absperrgitter", "Bauzaun", "Bauzaunfüsse", "Bauzaunklemmen", "Bauzaunblache", "Pylonen (Leitkegel)", "Leitbake", "Absperrband", "Warnleuchten", "Baustellenampel",
    "Verkehrstafeln", "Signalisation", "Fussgängersteg", "Überfahrtsplatten", "Stahlplatten", "Verkehrsleitwand", "Sandsäcke", "Baustellentafel",
    "Warnwesten", "Arbeitshandschuhe", "Schutzhelme", "Gehörschutz", "Schutzbrillen", "Erste-Hilfe-Material", "Feuerlöscher", "Absturzsicherung", "Geländer", "Leiter"
  ]],
  ["Betriebsmittel und Entsorgung", [
    "AdBlue", "Benzin bleifrei", "Alkylatbenzin", "2-Takt-Gemisch", "Motorenöl 15W-40", "Motorenöl 5W-30", "Hydrauliköl HLP 46", "Hydrauliköl HVLP 46", "Getriebeöl",
    "Kettenöl", "Schmierfett", "Kühlerfrostschutz", "Bremsflüssigkeit", "Scheibenwischwasser", "Reinigungsmittel", "Bremsenreiniger", "Rostlöser",
    "Markierspray", "Gasflasche Propan", "Ölbindemittel", "Ölbindematten", "Kanister", "Putzlappen", "Abfallsäcke",
    "Mulde 7 m³", "Mulde 10 m³", "Big Bag", "Entsorgung Bauschutt", "Entsorgung Aushub"
  ]],
  ["Ersatz- und Verschleissteile", [
    "Baggerzähne", "Zahnhalter", "Schneidkante Löffel", "Tieflöffel", "Grabenlöffel", "Meissel für Hydraulikhammer", "Hydraulikschlauch", "Schlauchkupplung",
    "Hydraulikfilter", "Luftfilter", "Ölfilter", "Kraftstofffilter", "Keilriemen", "Laufrolle", "Kettenglieder",
    "Reifen Radlader", "Reifen Dumper", "Reifen LKW", "Schaber für Walze", "Berieselungsdüsen Walze", "Kehrbürste", "Verschleissleisten Fertiger", "Förderschnecke Fertiger",
    "Mähmesser", "Messerbalken", "Trimmerfaden", "Trimmerkopf", "Sägekette", "Schwert für Kettensäge", "Zündkerze", "Sicherungen", "LED-Arbeitsscheinwerfer",
    "Starterbatterie", "Gummimatte für Rüttelplatte", "Rundschlinge", "Hebekette", "Stahlseil", "Spannband"
  ]],
  ["Kleinmaterial und Werkzeug", [
    "Schrauben", "Dübel", "Nägel", "Latten", "Kanthölzer", "Bretter", "Vermessungspflöcke", "Vermessungsnägel", "Fluchtstangen", "Maurerschnur",
    "Spaten", "Schaufel", "Pickel", "Rechen", "Schubkarre", "Eimer", "Kabelbinder", "Klebeband", "Montageschaum", "Silikon",
    "Trennscheiben", "Nasstrennscheibe", "Diamantscheibe", "Betonbohrer", "Schleifscheiben", "Sägeblätter"
  ]],
  ["Folien, Vliese, Abdichtung", [
    "Geotextil 200 g/m²", "Geotextil 300 g/m²", "Filtervlies", "Trennvlies", "Geogitter", "Wurzelsperre", "Teichfolie", "Baufolie", "Abdeckplane",
    "Dichtungsbahn", "Noppenbahn", "Drainagematte", "Abdichtungsbahn", "Schutzvlies", "Schutzmatte Gummi", "Erosionsschutzmatte", "Kokosmatte", "Jutenetz",
    "Wärmedämmung XPS", "Schaumglasschotter"
  ]]
];
