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
    d.goto(URL + "?modus=3d"); d.wait_for_timeout(800)
    check("Demo: Hinweis sichtbar", d.locator("#demoNote").is_visible())
    check("Demo: kein Login", not d.locator("#auth").is_visible())
    check("Demo: 6 Marker (5 Baustellen + Werkhof)", d.locator("#lmap .lm .site").count() == 6, str(d.locator("#lmap .lm .site").count()))
    check("Demo: Baustellenliste hat 5 Eintraege", d.locator("#siteList .item").count() == 5)
    d.fill("#siteSearch", "kanal")
    check("Demo: Suche findet 1", d.locator("#siteList .item").count() == 1)
    d.fill("#siteSearch", "")
    # Sparten-Filter: Mehrfachauswahl
    d.click('#filters [data-f="garten"]'); d.click('#filters [data-f="strasse"]')
    check("Filter: Garten und Strasse zusammen gewaehlt", d.locator("#siteList .item").count() == 4 and d.locator('#filters [data-f="garten"].active').count() == 1 and d.locator('#filters [data-f="strasse"].active').count() == 1 and d.locator('#filters [data-f="all"].active').count() == 0)
    check("Filter: Tiefbau-Baustelle ist ausgeblendet", d.locator("#siteList .item", has_text="Kanal Bahnhofstr.").count() == 0 and d.locator("#lmap .lm .site.dim").count() == 1)
    d.click('#filters [data-f="garten"]')
    check("Filter: Garten wieder abwaehlen", d.locator("#siteList .item").count() == 2)
    d.click('#filters [data-f="garten"]'); d.click('#filters [data-f="tief"]')
    check("Filter: alle drei gewaehlt = Alle", d.locator("#siteList .item").count() == 5 and d.locator('#filters [data-f="all"].active').count() == 1)
    d.click('#filters [data-f="tief"]'); d.click('#filters [data-f="all"]')
    check("Filter: Alle setzt zurueck", d.locator("#siteList .item").count() == 5 and d.locator("#filters button.active").count() == 1)
    d.click("#failBtn")
    check("Demo: Stoerung -> Banner", d.locator("#banner.show").count() == 1)
    check("Demo: Stoerung wird einmal gezaehlt", d.evaluate("incidents") == 1, str(d.evaluate("incidents")))
    check("Demo: kein Ton-Knopf und kein Audio", d.locator("#soundBtn").count() == 0 and d.evaluate("window.__audio") == 0)
    d.click("#addSiteBtn")
    d.fill("#f-name", "Testbaustelle"); d.select_option("#f-sparte", "garten")
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

    # Baustellen-Szene (SVG)
    check("Szene: jeder Marker hat eine Szene", d.locator("#lmap .lm .site .scene").count() == d.locator("#lmap .lm .site").count())
    kanal = d.locator("#lmap .lm .site", has_text="Kanal Bahnhofstr.")
    check("Szene: Kanal Bahnhofstr. zeigt 3 Maschinen", kanal.locator(".mach").count() == 3, str(kanal.locator(".mach").count()))
    check("Szene: Werkhof zeigt seine Maschinen gedimmt", d.locator("#lmap .lm .site.depot .mach.off").count() == 3)
    check("Szene: Stoerung -> eine Maschine blinkt rot", d.locator("#lmap .lm .site .mach.broken").count() >= 1 and d.locator("#lmap .lm .site .mach.broken").count() == d.locator("#lmap .lm .site .mach.broken .stc.broken").count())
    d.evaluate("""(()=>{
      for(let i=0;i<7;i++) machines.push({id:'x'+i,name:'Extra '+i,typ:'Dumper',sparte:'garten',site:'s1',status:'running',reason:''});
      machines.push({id:'xw',name:'Wartend',typ:'Mäher',sparte:'garten',site:'s1',status:'waiting',reason:'Material fehlt'});
      render();
    })()""")
    birke = d.locator("#lmap .lm .site", has_text="Birkenweg")
    check("Szene: mehr als 5 Maschinen -> 4 gezeichnet plus Zaehler", birke.locator(".mach").count() == 4 and "+" in birke.locator(".scene text").text_content(), birke.locator(".scene text").text_content())
    check("Szene: wartende Maschine bleibt sichtbar (Schlechteste zuerst)", birke.locator(".mach.waiting").count() >= 1)
    check("Szene: Zaehler zeigt echte Restzahl", birke.locator(".scene text").text_content() == "+" + str(d.evaluate("machines.filter(m=>m.site==='s1').length - 4")))
    d.evaluate("""(()=>{ machines.filter(m=>m.site==='s1').forEach(m=>{ m.site=null; m.status='off'; }); render(); })()""")
    check("Szene: ohne Maschinen keine Silhouetten", d.locator("#lmap .lm .site", has_text="Birkenweg").locator(".mach").count() == 0)
    # Bedarf (Demo)
    d.click("#siteList .item >> text=Kanal Bahnhofstr.")
    badge = lambda: d.locator("#lmap .lm .site", has_text="Kanal Bahnhofstr.").locator(".badge").inner_text()
    check("Bedarf: Kanal Bahnhofstr. zeigt 2 offene Eintraege aus der Demo", d.locator("#detail .need").count() == 2, str(d.locator("#detail .need").count()))
    check("Bedarf: Zaehler am Marker", badge() == "2", badge())
    check("Bedarf: Uebersicht zeigt alle 4 offenen", d.locator("#needsAll .item").count() == 4)
    check("Bedarf: Marker mit Bedarf hat die Tafel in der Szene, ohne Bedarf nicht",
          d.locator("#lmap .lm .site", has_text="Kanal Bahnhofstr.").locator('.scene rect[fill="#e6edf3"]').count() == 1
          and d.locator("#lmap .lm .site", has_text="Birkenweg").locator('.scene rect[fill="#e6edf3"]').count() == 0)
    d.fill("#needInput", "<b>5 Paletten</b> Pflaster"); d.click("#needAddBtn")
    check("Bedarf: neuer Eintrag erscheint, Text wird nicht als HTML gelesen", "<b>5 Paletten</b> Pflaster" in d.inner_text("#detail") and d.locator("#detail .need b").count() == 0)
    check("Bedarf: Zaehler steigt auf 3 und Feld ist wieder leer", badge() == "3" and d.input_value("#needInput") == "")
    d.fill("#needInput", "   "); d.click("#needAddBtn")
    check("Bedarf: leerer Eintrag wird ignoriert", d.locator("#detail .need").count() == 3)
    d.fill("#needInput", "Sand 3 Tonnen"); d.press("#needInput", "Enter")
    check("Bedarf: Enter speichert", d.locator("#detail .need", has_text="Sand 3 Tonnen").count() == 1)
    d.locator("#detail .need", has_text="Sand 3 Tonnen").locator("button", has_text="Erledigt").click()
    check("Bedarf: abhaken -> nicht mehr offen, Zaehler 3", badge() == "3" and d.locator("#detail .need.done").count() == 1 and d.locator("#needsAll .item", has_text="Sand 3 Tonnen").count() == 0)
    d.locator("#detail .need.done button", has_text="Wieder offen").click()
    check("Bedarf: Wieder offen", d.locator("#detail .need.done").count() == 0 and badge() == "4")
    d.click('#filters [data-f="garten"]')
    check("Bedarf: Sparten-Filter wirkt auf die Uebersicht (nur Gartenbau: 1)", d.locator("#needsAll .item").count() == 1)
    d.click('#filters [data-f="all"]')
    d.locator("#detail .need", has_text="Sand 3 Tonnen").locator("button", has_text="Löschen").click()
    d.locator("#detail .need", has_text="Sand 3 Tonnen").locator("button", has_text="Sicher").click()
    check("Bedarf: Loeschen mit zweitem Tipp", d.locator("#detail .need", has_text="Sand 3 Tonnen").count() == 0)
    d.screenshot(path="/tmp/" + os.path.basename(DIR + "/app_demo.png"), full_page=False)

    # ============================================================ LIVE
    print("=== LIVE-MODUS (Ersatz-Datenbank) ===")
    pg = new_page(b, True)
    pg.goto(URL + "?modus=3d"); pg.wait_for_timeout(800)
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
    pg.fill("#f-name", "Kanal Jona"); pg.select_option("#f-sparte", "tief")
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
    b0 = pg.evaluate("incidents")
    pg.click("#detail >> text=Defekt"); pg.wait_for_timeout(300)
    check("Live: Stoerung in Datenbank", pg.evaluate("window.__db.machines[0].status") == "broken")
    check("Live: Banner", pg.locator("#banner.show").count() == 1)
    check("Live: Stoerung genau einmal gezaehlt (Echo aus Echtzeit zaehlt nicht doppelt)", pg.evaluate("incidents") - b0 == 1, str(pg.evaluate("incidents") - b0))
    check("Live: Protokoll in Datenbank mit Name", any("Bagger A ausgefallen" in a["text"] and "Chef" in a["text"] for a in pg.evaluate("window.__db.activity")))
    pg.click("#detail >> text=Repariert"); pg.wait_for_timeout(300)
    check("Live: Repariert", pg.evaluate("window.__db.machines[0].status") == "running")

    # Material fehlt -> nachliefern
    pg.click("#detail >> text=Material fehlt"); pg.wait_for_timeout(200)
    check("Live: Material fehlt wartet", pg.evaluate("window.__db.machines[0].status") == "waiting" and "Material" in pg.evaluate("window.__db.machines[0].reason"))
    pg.click("#detail .mrow >> text=Nachgeliefert"); pg.wait_for_timeout(300)
    check("Live: Nachgeliefert -> laeuft wieder", pg.evaluate("window.__db.machines[0].status") == "running" and pg.evaluate("window.__db.machines[0].reason") == "")

    check("Live: keine Prozent-Anzeige fuer Material oder Diesel", "%" not in pg.inner_text("#detail") and pg.locator("#levelInput").count() == 0)
    pg.click("#detail .mrow >> text=Diesel fehlt"); pg.wait_for_timeout(300)
    check("Live: Diesel fehlt wartet", pg.evaluate("window.__db.machines[0].status") == "waiting" and pg.evaluate("window.__db.machines[0].reason") == "Diesel fehlt")
    pg.click("#detail .mrow >> text=Getankt"); pg.wait_for_timeout(300)
    check("Live: Getankt -> laeuft wieder", pg.evaluate("window.__db.machines[0].status") == "running")

    # Zwei Maschinen warten auf Material: ein Tipp auf Nachgeliefert gibt die ganze Baustelle frei
    pg.click("#addMachineBtn"); pg.fill("#m-name", "Bagger B"); pg.fill("#m-typ", "Minibagger")
    pg.click("text=Maschine speichern"); pg.wait_for_timeout(300)
    pg.click('#detail .mrow button:has-text("Material fehlt") >> nth=0'); pg.wait_for_timeout(200)
    pg.click('#detail .mrow button:has-text("Material fehlt") >> nth=0'); pg.wait_for_timeout(200)
    check("Live: zwei Maschinen warten auf Material", sum(1 for m in pg.evaluate("window.__db.machines") if m["status"] == "waiting") == 2)
    pg.click('#detail .mrow button:has-text("Nachgeliefert") >> nth=0'); pg.wait_for_timeout(400)
    check("Live: Nachgeliefert gibt alle wartenden Maschinen der Baustelle frei", all(m["status"] == "running" for m in pg.evaluate("window.__db.machines")))

    # Stoerung von einem anderen Handy (Echtzeit)
    b1 = pg.evaluate("incidents")
    pg.evaluate("(()=>{const m=window.__db.machines[0];const old=Object.assign({},m);m.status='broken';window.__db.emit('machines','UPDATE',m,old);})()")
    pg.wait_for_timeout(300)
    check("Live: fremde Stoerung zeigt Banner", pg.locator("#banner.show").count() == 1)
    check("Live: fremde Stoerung wird gezaehlt, ohne Ton", pg.evaluate("incidents") - b1 == 1 and pg.evaluate("window.__audio") == 0)
    pg.evaluate("(()=>{const m=window.__db.machines[0];const old=Object.assign({},m);m.status='running';window.__db.emit('machines','UPDATE',m,old);})()")
    # Neue Baustelle von einem anderen Handy erscheint
    pg.evaluate("(()=>{const r={id:'remote1',name:'Fremde Baustelle',sparte:'strasse',lat:47.3,lng:8.9};window.__db.sites.push(r);window.__db.emit('sites','INSERT',r);})()")
    pg.wait_for_timeout(300)
    check("Live: fremde Baustelle erscheint", pg.locator("#siteList .item", has_text="Fremde Baustelle").count() == 1)

    # Bedarf (Live)
    pg.click("#siteList .item >> text=Kanal Jona")
    jona = pg.evaluate("window.__db.sites.find(s=>s.name=='Kanal Jona').id")
    pg.fill("#needInput", "20 m³ Beton bis Mittwoch"); pg.press("#needInput", "Enter"); pg.wait_for_timeout(300)
    nd = pg.evaluate("window.__db.needs")
    check("Live: Bedarf in Datenbank mit Name und Baustelle", len(nd) == 1 and nd[0]["author"] == "Chef" and nd[0]["site_id"] == jona and nd[0]["text"] == "20 m³ Beton bis Mittwoch", str(nd))
    check("Live: Bedarf in der Liste und Zaehler am Marker", pg.locator("#detail .need").count() == 1 and pg.locator("#lmap .lm .site", has_text="Kanal Jona").locator(".badge").inner_text() == "1")
    check("Live: Protokoll nennt den Bedarf", any("Bedarf: 20 m³ Beton" in a["text"] for a in pg.evaluate("window.__db.activity")))
    pg.evaluate("((id)=>{const r={id:'rn1',site_id:id,text:'Kies 10 t',author:'Fremd',created_by:'other',created_at:new Date().toISOString(),done:false,done_by:'',done_at:null};window.__db.needs.push(r);window.__db.emit('needs','INSERT',r);})(%s)" % json.dumps(jona))
    pg.wait_for_timeout(300)
    check("Live: Bedarf von einem anderen Handy erscheint per Echtzeit", pg.locator("#detail .need", has_text="Kies 10 t").count() == 1 and pg.locator("#lmap .lm .site", has_text="Kanal Jona").locator(".badge").inner_text() == "2")
    check("Live: Admin darf fremden Bedarf loeschen", pg.locator("#detail .need", has_text="Kies 10 t").locator("button", has_text="Löschen").count() == 1)
    pg.locator("#detail .need", has_text="Kies 10 t").locator("button", has_text="Erledigt").click(); pg.wait_for_timeout(300)
    rn = [n for n in pg.evaluate("window.__db.needs") if n["id"] == "rn1"][0]
    check("Live: Abhaken wird gespeichert mit Name", rn["done"] is True and rn["done_by"] == "Chef")
    pg.locator("#detail .need", has_text="Kies 10 t").locator("button", has_text="Löschen").click()
    pg.locator("#detail .need", has_text="Kies 10 t").locator("button", has_text="Sicher").click(); pg.wait_for_timeout(300)
    check("Live: Loeschen entfernt den Bedarf aus der Datenbank", len(pg.evaluate("window.__db.needs")) == 1)
    pg.evaluate("window.__db.failNext={table:'needs',msg:'relation needs does not exist'}")
    pg.evaluate("loadAll()"); pg.wait_for_timeout(300)
    check("Live: fehlt die Tabelle needs, bricht nichts ab und ein Hinweis erscheint", "Datenbank-Update" in pg.inner_text("#detail") and pg.locator("#siteList .item").count() >= 2)
    pg.evaluate("loadAll()"); pg.wait_for_timeout(300)
    check("Live: nach dem Update ist der Bedarf wieder da", pg.locator("#needInput").count() == 1 and pg.locator("#detail .need").count() == 1)

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
    pg.click("#siteList .item >> text=Kanal Jona"); pg.wait_for_timeout(200)
    check("Live: Mitarbeiter sieht fremden Bedarf, aber keinen Loeschen-Knopf dafuer", pg.locator("#detail .need").count() == 1 and pg.locator("#detail .need button", has_text="Löschen").count() == 0)
    pg.fill("#needInput", "Eigener Eintrag"); pg.press("#needInput", "Enter"); pg.wait_for_timeout(300)
    check("Live: Mitarbeiter darf eigenen Bedarf schreiben und loeschen", pg.locator("#detail .need", has_text="Eigener Eintrag").locator("button", has_text="Löschen").count() == 1)
    pg.locator("#detail .need", has_text="Eigener Eintrag").locator("button", has_text="Löschen").click()
    pg.locator("#detail .need", has_text="Eigener Eintrag").locator("button", has_text="Sicher").click(); pg.wait_for_timeout(300)
    check("Live: eigener Bedarf geloescht", pg.locator("#detail .need", has_text="Eigener Eintrag").count() == 0)
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
    mob.goto(URL + "?modus=leicht"); mob.wait_for_timeout(500)
    mob.fill("#aMail", "chef@firma.test"); mob.fill("#aPass", "x")
    check("Handy: Login ohne seitliches Scrollen", not mob.evaluate("document.documentElement.scrollWidth > window.innerWidth"))
    mob.evaluate("window.__db.users['chef@firma.test']={id:'u1',email:'chef@firma.test',password:'langes-passwort'};window.__db.profiles.push({id:'u1',email:'chef@firma.test',name:'Chef',role:'admin',approved:true});window.__db.sites.push({id:'a',name:'Testweg',sparte:'tief',lat:47.23,lng:8.83});window.__db.machines.push({id:'m',name:'Bagger',typ:'Bagger',sparte:'tief',site_id:'a',status:'running',reason:''});")
    mob.fill("#aPass", "langes-passwort"); mob.click("#authGo"); mob.wait_for_timeout(600)
    check("Handy: Dashboard ohne seitliches Scrollen", not mob.evaluate("document.documentElement.scrollWidth > window.innerWidth"))
    mob.click("#addSiteBtn")
    check("Handy: Formular ohne seitliches Scrollen", not mob.evaluate("document.documentElement.scrollWidth > window.innerWidth"))
    mob.screenshot(path="/tmp/" + os.path.basename(DIR + "/app_live_form_handy.png"))
    mob.click("#modal >> text=Schliessen")
    mob.screenshot(path="/tmp/" + os.path.basename(DIR + "/app_live_handy.png"), full_page=True)

    # ============================================================ MODI
    print("=== MODI (Leicht / 3D) ===")
    def raw_page(w, h, cores=8, mem=8, saved=None, stubs=False, urls=None):
        ctx = b.new_context(viewport={"width": w, "height": h}, screen={"width": w, "height": h})
        pg2 = ctx.new_page()
        pg2.on("pageerror", lambda e: errors.append(str(e)))
        if urls is not None: pg2.on("request", lambda r: urls.append(r.url))
        pg2.route("**/unpkg.com/**", lambda r: r.abort())
        pg2.route("**/config.js", lambda r: r.fulfill(body="window.APP_CONFIG={};", content_type="application/javascript"))
        init = "Object.defineProperty(navigator,'hardwareConcurrency',{get:()=>%d});Object.defineProperty(navigator,'deviceMemory',{get:()=>%d});" % (cores, mem)
        if saved: init += "try{localStorage.setItem('modus','%s')}catch(e){}" % saved
        pg2.add_init_script(init + (STUBS if stubs else ""))
        return pg2

    g = raw_page(1280, 800); g.goto(URL); g.wait_for_timeout(300)
    check("Modus: Computer (grosser Bildschirm, 8 Kerne) startet im 3D-Modus", g.evaluate("MODE") == "3d" and g.locator("#modeBtn").inner_text() == "Modus: 3D")
    g = raw_page(390, 800); g.goto(URL); g.wait_for_timeout(300)
    check("Modus: Handy (kleiner Bildschirm) startet im Leicht-Modus", g.evaluate("MODE") == "leicht" and g.evaluate("document.body.classList.contains('leicht')"))
    g = raw_page(1280, 800, cores=2); g.goto(URL); g.wait_for_timeout(300)
    check("Modus: Geraet mit 2 Kernen startet im Leicht-Modus", g.evaluate("MODE") == "leicht")
    g = raw_page(1280, 800, mem=2); g.goto(URL); g.wait_for_timeout(300)
    check("Modus: Geraet mit 2 GB Speicher startet im Leicht-Modus", g.evaluate("MODE") == "leicht")
    g = raw_page(390, 800, saved="3d"); g.goto(URL); g.wait_for_timeout(300)
    check("Modus: gespeicherte Wahl gewinnt gegen die Erkennung", g.evaluate("MODE") == "3d")
    g = raw_page(390, 800, saved="3d"); g.goto(URL + "?modus=leicht"); g.wait_for_timeout(300)
    check("Modus: Adresszusatz ?modus=leicht gewinnt gegen gespeicherte Wahl", g.evaluate("MODE") == "leicht")

    # Der Leicht-Modus laedt MapLibre gar nicht, der 3D-Modus schon
    urls = []
    g = raw_page(1280, 800, urls=urls); g.goto(URL + "?modus=leicht"); g.wait_for_timeout(600)
    check("Leicht: MapLibre wird nicht geladen, keine Karte", not any("maplibre" in u for u in urls) and g.evaluate("!!lmap") is False and g.locator("canvas").count() == 0)
    check("Leicht: Skizze mit Szenen ist da (5 Baustellen + Werkhof)", g.locator("#sites .site .scene").count() == 6, str(g.locator("#sites .site .scene").count()))
    urls3 = []
    g3 = raw_page(1280, 800, urls=urls3); g3.goto(URL + "?modus=3d"); g3.wait_for_timeout(600)
    check("3D: MapLibre wird erst im 3D-Modus angefordert", any("maplibre" in u for u in urls3))

    # Umschalten zur Laufzeit (mit Ersatz-Karte)
    m = raw_page(1280, 800, stubs=True); m.goto(URL + "?modus=3d"); m.wait_for_timeout(700)
    check("Wechsel: 3D zeigt die Karte mit 6 Markern", m.locator("#lmap .lm .site").count() == 6 and m.locator("#map.real").count() == 1)
    m.click("#modeBtn"); m.wait_for_timeout(300)
    check("Wechsel: auf Leicht -> Karte abgebaut, Skizze mit 6 Markern", m.evaluate("!!lmap") is False and m.locator("#lmap .lm").count() == 0 and m.locator("#sites .site").count() == 6 and m.locator("#map.real").count() == 0)
    check("Wechsel: Knopf zeigt Leicht, Wahl wird gemerkt", m.locator("#modeBtn").inner_text() == "Modus: Leicht" and m.evaluate("localStorage.getItem('modus')") == "leicht")
    check("Wechsel: Auswahl der Baustelle bleibt", m.locator("#detail strong").inner_text() == "Kanal Bahnhofstr.")
    m.click("#modeBtn"); m.wait_for_timeout(500)
    check("Wechsel: zurueck auf 3D -> Karte wieder da", m.evaluate("!!lmap") is True and m.locator("#lmap .lm .site").count() == 6)
    m.click("#modeBtn"); m.goto(URL); m.wait_for_timeout(500)
    check("Wechsel: nach Neuladen bleibt Leicht (gemerkt)", m.evaluate("MODE") == "leicht")

    # Leicht-Modus: bei vielen Baustellen werden Szenen erst beim Hinscrollen gezeichnet
    l = raw_page(390, 700, stubs=True); l.goto(URL + "?modus=leicht"); l.wait_for_timeout(500)
    l.evaluate("""(()=>{ for(let i=0;i<14;i++) sites.push({id:'z'+i,name:'Zusatz '+i,sparte:'tief',lat:47.2+i/100,lng:8.8}); render(); })()""")
    l.wait_for_timeout(300)
    ph = l.locator("#sites .site .scene-ph").count()
    check("Leicht: viele Baustellen -> Szenen ausserhalb des Bildschirms sind noch Platzhalter", ph > 0 and l.locator("#sites .site .scene:not(.scene-ph)").count() > 0, str(ph))
    for i in range(14):                                    # wie ein Mensch: schrittweise nach unten scrollen
        l.evaluate("window.scrollBy(0, 300)"); l.wait_for_timeout(150)
    l.wait_for_timeout(300)
    check("Leicht: nach dem Hinscrollen sind alle Szenen gezeichnet", l.locator("#sites .site .scene-ph").count() == 0, str(l.locator("#sites .site .scene-ph").count()))
    check("Leicht: Handy ohne seitliches Scrollen", not l.evaluate("document.documentElement.scrollWidth > window.innerWidth"))
    b.close()

print()
print("Fehler im Browser:", errors)
bad = [n for n, ok in checks if not ok]
print("Ergebnis: %d von %d Pruefungen bestanden" % (len(checks) - len(bad), len(checks)))
if bad: print("Nicht bestanden:", bad)
