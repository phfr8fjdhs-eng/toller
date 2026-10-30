import os
from playwright.sync_api import sync_playwright
import json

DIR = os.path.dirname(os.path.abspath(__file__))
URL = "file://" + os.path.join(os.path.dirname(DIR), "public", "index.html")
STUBS = open(DIR + "/stubs.js", encoding="utf-8").read()
CONFIG = 'window.APP_CONFIG={supabaseUrl:"https://x.supabase.co",supabaseKey:"anon-test",depot:{lat:47.234,lng:8.86}};'

errors = []
checks = []

def check(name, cond, extra=""):
    checks.append((name, bool(cond)))
    print(("OK    " if cond else "FEHLER"), name, extra)

def new_page(b, live, w=1280, h=900):
    pg = b.new_page(viewport={"width": w, "height": h})
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
    pg.route("**/unpkg.com/**", lambda r: r.abort())
    pg.route("**/config.js", lambda r: r.fulfill(body=CONFIG if live else "window.APP_CONFIG={};", content_type="application/javascript"))
    pg.route("**/api3.geo.admin.ch/**", lambda r: r.fulfill(
        body=json.dumps({"results": [{"attrs": {"label": "<b>Bahnhofstrasse 1</b> 8645 Jona", "lat": 47.2271, "lon": 8.8404}}]}),
        content_type="application/json", headers={"access-control-allow-origin": "*"}))
    pg.add_init_script(STUBS)
    return pg

with sync_playwright() as p:
    b = p.chromium.launch()

    # ============================================================ DEMO
    print("=== DEMO-MODUS ===")
    d = new_page(b, False)
    d.goto(URL); d.wait_for_timeout(800)
    check("Demo: Hinweis sichtbar", d.locator("#demoNote").is_visible())
    check("Demo: kein Login", not d.locator("#auth").is_visible())
    check("Demo: 6 Marker (5 Baustellen + Werkhof)", d.locator("#lmap .lm .site").count() == 6, str(d.locator("#lmap .lm .site").count()))
    check("Demo: Baustellenliste hat 5 Eintraege", d.locator("#siteList .item").count() == 5)
    d.fill("#siteSearch", "kanal")
    check("Demo: Suche findet 1", d.locator("#siteList .item").count() == 1)
    d.fill("#siteSearch", "")
    d.click("#failBtn")
    check("Demo: Stoerung -> Banner", d.locator("#banner.show").count() == 1)
    check("Demo: Ton einmal (2 Toene)", d.evaluate("window.__beeps") == 2, str(d.evaluate("window.__beeps")))
    d.click("#addSiteBtn")
    d.fill("#f-name", "Testbaustelle"); d.select_option("#f-sparte", "garten"); d.fill("#f-mat", "Humus")
    d.fill("#f-lat", "47.24"); d.fill("#f-lng", "8.83")
    d.click("text=Baustelle speichern")
    check("Demo: neue Baustelle in Liste", d.locator("#siteList .item", has_text="Testbaustelle").count() == 1)
    check("Demo: Detail zeigt neue Baustelle", "Testbaustelle" in d.inner_text("#detail"))
    d.click("#addMachineBtn")
    d.fill("#m-name", "Testbagger"); d.fill("#m-typ", "Bagger")
    d.click("text=Maschine speichern")
    check("Demo: Maschine auf der Baustelle", "Testbagger" in d.inner_text("#detail"))
    d.click("#addSiteBtn"); d.click("text=Baustelle speichern")
    check("Demo: leeres Formular wird abgelehnt", "Bitte einen Namen" in d.inner_text("#modal"))
    d.click("#modal >> text=Schliessen")
    d.screenshot(path="/tmp/" + os.path.basename(DIR + "/app_demo.png"), full_page=False)

    # ============================================================ LIVE
    print("=== LIVE-MODUS (Ersatz-Datenbank) ===")
    pg = new_page(b, True)
    pg.goto(URL); pg.wait_for_timeout(800)
    check("Live: Login-Fenster sichtbar", pg.locator("#auth").is_visible())
    check("Live: keine Demo-Daten", pg.locator("#lmap .lm .site").count() <= 1 and pg.locator("#siteList .item").count() == 0)
    check("Live: kein Demo-Hinweis", not pg.locator("#demoNote").is_visible())

    # Registrierung: erste Person wird Admin
    pg.click("#authToggle")
    pg.fill("#aName", "Chef"); pg.fill("#aMail", "chef@firma.test"); pg.fill("#aPass", "kurz")
    pg.click("#authGo")
    check("Live: kurzes Passwort wird abgelehnt", "mindestens 8" in pg.inner_text("#authMsg"))
    pg.fill("#aPass", "langes-passwort")
    pg.click("#authGo"); pg.wait_for_timeout(600)
    check("Live: nach Registrierung eingeloggt", not pg.locator("#auth").is_visible() and not pg.locator("#pending").is_visible())
    check("Live: erste Person ist Admin (Benutzer-Knopf)", pg.locator("#usersBtn").is_visible())
    check("Live: Verbindung 'live' angezeigt", "live" in pg.inner_text("#conn"))
    check("Live: Leer-Hinweis", "Noch keine Baustellen" in pg.inner_text("#detail"))

    # Baustelle ueber Adresssuche
    pg.click("#addSiteBtn")
    pg.fill("#f-name", "Kanal Jona"); pg.select_option("#f-sparte", "tief"); pg.fill("#f-mat", "Kies"); pg.fill("#f-level", "60")
    pg.fill("#f-addr", "Bahnhofstrasse Jona"); pg.click("#modal >> text=Suchen"); pg.wait_for_timeout(300)
    check("Live: Adresssuche zeigt Treffer ohne HTML-Tags", pg.locator("#modal .results button").count() == 1 and "<b>" not in pg.inner_text("#modal .results"))
    pg.click("#modal .results button")
    check("Live: Treffer setzt Koordinaten", pg.input_value("#f-lat") == "47.22710" and pg.input_value("#f-lng") == "8.84040")
    pg.click("text=Baustelle speichern"); pg.wait_for_timeout(300)
    check("Live: Baustelle in Datenbank", len(pg.evaluate("window.__db.sites")) == 1)
    check("Live: Baustelle in Liste", pg.locator("#siteList .item", has_text="Kanal Jona").count() == 1)

    # Baustelle ueber Kartenklick
    pg.click("#addSiteBtn"); pg.fill("#f-name", "Park Nord")
    pg.click("text=Ort auf der Karte wählen")
    check("Live: Auswahl-Leiste sichtbar", pg.locator("#pickBar").is_visible() and not pg.locator("#modal").count())
    pg.evaluate("window.__mapClick(47.25, 8.85)"); pg.wait_for_timeout(200)
    check("Live: Kartenklick fuellt Formular, Name bleibt", pg.input_value("#f-lat") == "47.25000" and pg.input_value("#f-name") == "Park Nord")
    pg.click("text=Baustelle speichern"); pg.wait_for_timeout(300)
    check("Live: 2 Baustellen in Datenbank", len(pg.evaluate("window.__db.sites")) == 2)

    # Ungueltige Koordinaten
    pg.click("#addSiteBtn"); pg.fill("#f-name", "X"); pg.fill("#f-lat", "999"); pg.fill("#f-lng", "8")
    pg.click("text=Baustelle speichern")
    check("Live: ungueltiger Ort wird abgelehnt", "gültigen Ort" in pg.inner_text("#modal") and len(pg.evaluate("window.__db.sites")) == 2)
    pg.click("#modal >> text=Schliessen")

    # Maschine
    pg.click("#siteList .item >> nth=0")
    pg.click("#addMachineBtn"); pg.fill("#m-name", "Bagger A"); pg.fill("#m-typ", "Bagger")
    pg.click("text=Maschine speichern"); pg.wait_for_timeout(300)
    mach = pg.evaluate("window.__db.machines")
    check("Live: Maschine gespeichert, laeuft auf Baustelle", len(mach) == 1 and mach[0]["status"] == "running" and mach[0]["site_id"] is not None)

    # Stoerung melden
    b0 = pg.evaluate("window.__beeps")
    pg.click("#detail >> text=Defekt"); pg.wait_for_timeout(300)
    check("Live: Stoerung in Datenbank", pg.evaluate("window.__db.machines[0].status") == "broken")
    check("Live: Banner", pg.locator("#banner.show").count() == 1)
    check("Live: Ton genau einmal (Echo aus Echtzeit loest nicht doppelt aus)", pg.evaluate("window.__beeps") - b0 == 2, str(pg.evaluate("window.__beeps") - b0))
    check("Live: Protokoll in Datenbank mit Name", any("Bagger A ausgefallen" in a["text"] and "Chef" in a["text"] for a in pg.evaluate("window.__db.activity")))
    pg.click("#detail >> text=Repariert"); pg.wait_for_timeout(300)
    check("Live: Repariert", pg.evaluate("window.__db.machines[0].status") == "running")

    # Material fehlt -> nachliefern
    pg.click("#detail >> text=Material fehlt"); pg.wait_for_timeout(200)
    check("Live: Material fehlt wartet", pg.evaluate("window.__db.machines[0].status") == "waiting" and "Material" in pg.evaluate("window.__db.machines[0].reason"))
    pg.click("#detail .mrow >> text=Nachgeliefert"); pg.wait_for_timeout(300)
    check("Live: Nachgeliefert -> laeuft, Material 100", pg.evaluate("window.__db.machines[0].status") == "running" and pg.evaluate("window.__db.sites.find(s=>s.name=='Kanal Jona').material_level") == 100)

    pg.click("#detail .mrow >> text=Material fehlt"); pg.wait_for_timeout(200)
    pg.fill("#levelInput", "80"); pg.press("#levelInput", "Tab"); pg.wait_for_timeout(400)
    check("Live: Fuellstand per Eingabe gibt wartende Maschine frei", pg.evaluate("window.__db.machines[0].status") == "running" and pg.evaluate("window.__db.sites.find(s=>s.name=='Kanal Jona').material_level") == 80)
    pg.click("#detail .mrow >> text=Material fehlt"); pg.wait_for_timeout(200)
    pg.click("#detail >> text=Nachgeliefert (100%)"); pg.wait_for_timeout(400)
    check("Live: Knopf 'Nachgeliefert (100%)' gibt wartende Maschine frei", pg.evaluate("window.__db.machines[0].status") == "running" and pg.evaluate("window.__db.sites.find(s=>s.name=='Kanal Jona').material_level") == 100)

    # Stoerung von einem anderen Handy (Echtzeit)
    b1 = pg.evaluate("window.__beeps")
    pg.evaluate("(()=>{const m=window.__db.machines[0];const old=Object.assign({},m);m.status='broken';window.__db.emit('machines','UPDATE',m,old);})()")
    pg.wait_for_timeout(300)
    check("Live: fremde Stoerung zeigt Banner", pg.locator("#banner.show").count() == 1)
    check("Live: fremde Stoerung loest Ton aus", pg.evaluate("window.__beeps") - b1 == 2)
    pg.evaluate("(()=>{const m=window.__db.machines[0];const old=Object.assign({},m);m.status='running';window.__db.emit('machines','UPDATE',m,old);})()")
    # Neue Baustelle von einem anderen Handy erscheint
    pg.evaluate("(()=>{const r={id:'remote1',name:'Fremde Baustelle',sparte:'strasse',material_name:'Asphalt',material_level:50,lat:47.3,lng:8.9};window.__db.sites.push(r);window.__db.emit('sites','INSERT',r);})()")
    pg.wait_for_timeout(300)
    check("Live: fremde Baustelle erscheint", pg.locator("#siteList .item", has_text="Fremde Baustelle").count() == 1)

    # Fehler beim Speichern
    pg.evaluate("window.__db.failNext={table:'machines',msg:'Netzwerkfehler'}")
    pg.click("#detail >> text=Defekt"); pg.wait_for_timeout(400)
    check("Live: Speicherfehler wird gemeldet", pg.locator("#toast.err").count() == 1 and "Netzwerkfehler" in pg.inner_text("#toast"))
    check("Live: nach Speicherfehler wieder Stand der Datenbank", pg.evaluate("window.__db.machines[0].status") == "running")

    pg.screenshot(path="/tmp/" + os.path.basename(DIR + "/app_live_admin.png"), full_page=False)

    # Zweite Person: nicht freigegeben
    pg.click("#logoutBtn"); pg.wait_for_timeout(300)
    check("Live: nach Abmelden wieder Login, Daten weg", pg.locator("#auth").is_visible() and pg.locator("#siteList .item").count() == 0)
    pg.click("#authToggle")
    pg.fill("#aName", "Neuling"); pg.fill("#aMail", "neu@firma.test"); pg.fill("#aPass", "langes-passwort")
    pg.click("#authGo"); pg.wait_for_timeout(500)
    check("Live: zweite Person wartet auf Freigabe", pg.locator("#pending").is_visible())
    check("Live: ohne Freigabe keine Daten", pg.locator("#siteList .item").count() == 0 and "Noch keine" in pg.inner_text("#siteList") or pg.locator("#siteList .item").count() == 0)
    check("Live: ohne Freigabe kein Benutzer-Knopf", not pg.locator("#usersBtn").is_visible())
    # Admin gibt frei (direkt in Ersatz-Datenbank), Person prueft neu
    pg.evaluate("window.__db.profiles.find(p=>p.email=='neu@firma.test').approved=true")
    pg.click("#pendingCheck"); pg.wait_for_timeout(500)
    check("Live: nach Freigabe sieht Mitarbeiter Daten", not pg.locator("#pending").is_visible() and pg.locator("#siteList .item").count() >= 2)
    check("Live: Mitarbeiter hat keinen Benutzer-Knopf", not pg.locator("#usersBtn").is_visible())
    check("Live: Mitarbeiter sieht keine Loeschen-Knoepfe", pg.locator("#detail >> text=Löschen").count() == 0 and pg.locator("text=Baustelle löschen").count() == 0)

    # Admin: Benutzerverwaltung und Loeschen
    pg.click("#logoutBtn"); pg.wait_for_timeout(300)
    pg.fill("#aMail", "chef@firma.test"); pg.fill("#aPass", "falsch-falsch")
    pg.click("#authGo"); pg.wait_for_timeout(300)
    check("Live: falsches Passwort -> deutsche Meldung", "stimmt nicht" in pg.inner_text("#authMsg"))
    pg.fill("#aPass", "langes-passwort"); pg.click("#authGo"); pg.wait_for_timeout(600)
    check("Live: Admin wieder da", pg.locator("#usersBtn").is_visible())
    pg.click("#usersBtn"); pg.wait_for_timeout(300)
    check("Live: Benutzerliste zeigt 2 Personen", pg.locator("#modal .urow").count() == 2)
    pg.click("#modal >> text=Sperren"); pg.wait_for_timeout(300)
    check("Live: Sperren wirkt in Datenbank", pg.evaluate("window.__db.profiles.find(p=>p.email=='neu@firma.test').approved") is False)
    pg.click("#modal >> text=Schliessen")

    pg.click("#siteList .item >> text=Kanal Jona")
    pg.click("#detail >> text=Baustelle löschen")
    check("Live: Loeschen braucht zweiten Tipp", len(pg.evaluate("window.__db.sites")) == 3 and "Sicher" in pg.inner_text("#detail"))
    pg.click("#detail >> text=Sicher"); pg.wait_for_timeout(400)
    check("Live: Baustelle geloescht", pg.evaluate("window.__db.sites.some(s=>s.name=='Kanal Jona')") is False)
    check("Live: Maschine der Baustelle im Werkhof", pg.evaluate("window.__db.machines[0].site_id") is None and pg.evaluate("window.__db.machines[0].status") == "off")

    # Handy-Ansicht
    mob = new_page(b, True, 390, 800)
    mob.goto(URL); mob.wait_for_timeout(500)
    mob.fill("#aMail", "chef@firma.test"); mob.fill("#aPass", "x")
    check("Handy: Login ohne seitliches Scrollen", not mob.evaluate("document.documentElement.scrollWidth > window.innerWidth"))
    mob.evaluate("window.__db.users['chef@firma.test']={id:'u1',email:'chef@firma.test',password:'langes-passwort'};window.__db.profiles.push({id:'u1',email:'chef@firma.test',name:'Chef',role:'admin',approved:true});window.__db.sites.push({id:'a',name:'Testweg',sparte:'tief',material_name:'Kies',material_level:70,lat:47.23,lng:8.83});window.__db.machines.push({id:'m',name:'Bagger',typ:'Bagger',sparte:'tief',site_id:'a',status:'running',tank:80,reason:''});")
    mob.fill("#aPass", "langes-passwort"); mob.click("#authGo"); mob.wait_for_timeout(600)
    check("Handy: Dashboard ohne seitliches Scrollen", not mob.evaluate("document.documentElement.scrollWidth > window.innerWidth"))
    mob.click("#addSiteBtn")
    check("Handy: Formular ohne seitliches Scrollen", not mob.evaluate("document.documentElement.scrollWidth > window.innerWidth"))
    mob.screenshot(path="/tmp/" + os.path.basename(DIR + "/app_live_form_handy.png"))
    mob.click("#modal >> text=Schliessen")
    mob.screenshot(path="/tmp/" + os.path.basename(DIR + "/app_live_handy.png"), full_page=True)
    b.close()

print()
print("Fehler im Browser:", errors)
bad = [n for n, ok in checks if not ok]
print("Ergebnis: %d von %d Pruefungen bestanden" % (len(checks) - len(bad), len(checks)))
if bad: print("Nicht bestanden:", bad)
