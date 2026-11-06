# Speicher-Test: misst im Browser, wie viel Arbeitsspeicher die Seite braucht (JavaScript-Heap und Seitenelemente).
# Zweck: Der Leicht-Modus muss auf alten Handys laufen. Die Grenzen unten sind absichtlich eng; wer sie hebt, muss es begruenden.
# Aufruf: python3 tests/speicher_test.py   (braucht Playwright, wie app_test.py)
import os, json
from playwright.sync_api import sync_playwright

DIR = os.path.dirname(os.path.abspath(__file__))
URL = "file://" + os.path.join(os.path.dirname(DIR), "public", "index.html")
STUBS = open(DIR + "/stubs.js", encoding="utf-8").read()
NO_RANDOM = "Math.random = () => 0.5;"
CONFIG = 'window.APP_CONFIG={supabaseUrl:"https://x.supabase.co",supabaseKey:"anon-test",depot:{lat:47.234,lng:8.86}};'

# Grenzen (Leicht-Modus, 390 x 800, nach dem Anmelden mit der Datenmenge unten). Gemessen: ca. 1.8 MB und 3100 Elemente, dazu Reserve.
# Wichtig: Gemessen wird der JavaScript-Heap und die Zahl der Seitenelemente. Grafikspeicher (WebGL, Kartenkacheln) wird hier NICHT gemessen:
# MapLibre und three.js sind im Test nur Ersatz. Dass der Leicht-Modus sie nie laedt, prueft die erste Pruefung unten.
LIMITS = {"heap_mb": 4.0, "nodes": 4000}
SITES, PER_SITE, NEEDS = 60, 3, 90

results = []
def check(name, ok, extra=""):
    results.append((name, bool(ok))); print(("OK    " if ok else "FEHLER"), name, extra)

def measure(b, mode, n_sites, per_site, n_needs, history=False):
    ctx = b.new_context(viewport={"width": 390, "height": 800})
    pg = ctx.new_page()
    reqs = []
    pg.on("request", lambda r: reqs.append(r.url))
    pg.route("**/unpkg.com/**", lambda r: r.abort())
    pg.route("**/config.js", lambda r: r.fulfill(body=CONFIG, content_type="application/javascript"))
    pg.route("**/api3.geo.admin.ch/**", lambda r: r.abort())
    pg.add_init_script(NO_RANDOM + STUBS)
    cdp = ctx.new_cdp_session(pg); cdp.send("Performance.enable")
    pg.goto(URL + "?modus=" + mode); pg.wait_for_timeout(500)
    pg.evaluate("""([ns, per, nn]) => {
      const db = window.__db, sp = ['garten','strasse','tief'];
      db.users['chef@firma.test'] = {id:'u1', email:'chef@firma.test', password:'langes-passwort'};
      db.profiles.push({id:'u1', email:'chef@firma.test', name:'Chef', role:'admin', approved:true});
      for(let i = 0; i < ns; i++){
        db.sites.push({id:'s'+i, name:'Baustelle '+i+' Musterweg', sparte:sp[i%3], lat:47.2+(i%10)*0.01, lng:8.8+Math.floor(i/10)*0.01});
        for(let j = 0; j < per; j++) db.machines.push({id:'m'+i+'_'+j, name:'Maschine '+i+'-'+j, typ:['Bagger','Walze','Dumper','LKW'][j%4], sparte:sp[i%3], site_id:'s'+i, status:(i+j)%11===0?'waiting':'running', reason:(i+j)%11===0?'Diesel fehlt':''});
      }
      for(let k = 0; k < nn; k++) db.needs.push({id:'n'+k, site_id:'s'+(k%ns), text:'Kies 0/32 ca. 20 m3 bis Mittwoch '+k, author:'Chef', created_by:'u1', done:false, done_by:'', created_at:new Date().toISOString()});
    }""", [n_sites, per_site, n_needs])
    pg.fill("#aMail", "chef@firma.test"); pg.fill("#aPass", "langes-passwort"); pg.click("#authGo"); pg.wait_for_timeout(900)
    cdp.send("HeapProfiler.collectGarbage")
    m = {x["name"]: x["value"] for x in cdp.send("Performance.getMetrics")["metrics"]}
    info = {
        "heap_mb": m["JSHeapUsedSize"] / 1048576.0,
        "nodes": int(m["Nodes"]),
        "listeners": int(m["JSEventListeners"]),
        "scenes": pg.locator("svg.scene").count(),     # echte Szenen; Platzhalter (div.scene-ph) zählen nicht
        "sites": pg.locator("#siteList .item").count(),
        "heavy_requests": [u for u in reqs if "maplibre" in u or "three" in u],
        "map_loaded": pg.evaluate("typeof window.maplibregl !== 'undefined' && !!document.querySelector('#lmap .lm')") if mode == "leicht" else None,
    }
    if history:      # Verlauf mit 600 Eintraegen oeffnen und wieder schliessen: Seitenelemente zaehlen
        pg.evaluate("""() => { const d = window.__db, T = Date.now(); for(let i = 0; i < 600; i++) d.downtimes.push({id:d.seq++, machine_id:'m'+(i%50)+'_0', machine_name:'Maschine '+(i%50)+'-0', typ:'Bagger', site_name:'Baustelle '+(i%50)+' Musterweg', kind:i%3?'broken':'waiting', reason:i%3?'':'Diesel fehlt', reported_name:'Chef', started_at:new Date(T-(i+10)*3600000).toISOString(), ended_at:new Date(T-(i+9)*3600000).toISOString()}); }""")
        def nodes():    # erst Speicher bereinigen, sonst zählen abgelegte, noch nicht freigegebene Elemente mit
            cdp.send("HeapProfiler.collectGarbage"); cdp.send("HeapProfiler.collectGarbage")
            return int({x["name"]: x["value"] for x in cdp.send("Performance.getMetrics")["metrics"]}["Nodes"])
        info["nodes_before_hist"] = nodes(); info["dom_before_hist"] = pg.evaluate("document.querySelectorAll('*').length")
        pg.click("#historyBtn"); pg.wait_for_timeout(500)
        info["nodes_hist_open"] = nodes(); info["hist_dom"] = pg.evaluate("document.querySelectorAll('#modal *').length"); info["hist_rows"] = pg.locator("#histBox .hrow .hk").count()
        pg.click("#modal >> text=Schliessen"); pg.wait_for_timeout(200)
        info["nodes_hist_closed"] = nodes()
        info["dom_after_close"] = pg.evaluate("document.querySelectorAll('*').length")
        for _ in range(2):         # zweimal öffnen und schliessen: es darf nichts wachsen
            pg.click("#historyBtn"); pg.wait_for_timeout(400); pg.click("#modal >> text=Schliessen"); pg.wait_for_timeout(200)
        info["nodes_hist_closed3"] = nodes()
    ctx.close()
    return info

with sync_playwright() as p:
    b = p.chromium.launch(args=["--js-flags=--expose-gc"])
    klein = measure(b, "leicht", 5, 3, 5)
    gross = measure(b, "leicht", SITES, PER_SITE, NEEDS, history=True)
    d3 = measure(b, "3d", SITES, PER_SITE, NEEDS)
    b.close()

print()
print("Leicht, 5 Baustellen:       %.1f MB Heap, %d Elemente, %d Szenen" % (klein["heap_mb"], klein["nodes"], klein["scenes"]))
print("Leicht, %d Baustellen:      %.1f MB Heap, %d Elemente, %d Szenen, %d Listen-Eintraege" % (SITES, gross["heap_mb"], gross["nodes"], gross["scenes"], gross["sites"]))
print("3D,     %d Baustellen:      %.1f MB Heap, %d Elemente (zum Vergleich, ohne echte Karte)" % (SITES, d3["heap_mb"], d3["nodes"]))
print()
check("Leicht: lädt weder MapLibre noch three.js", not gross["heavy_requests"], str(gross["heavy_requests"]))
check("Leicht: Heap unter %.0f MB bei %d Baustellen und %d Maschinen" % (LIMITS["heap_mb"], SITES, SITES * PER_SITE), gross["heap_mb"] < LIMITS["heap_mb"], "%.1f MB" % gross["heap_mb"])
check("Leicht: höchstens %d Seitenelemente" % LIMITS["nodes"], gross["nodes"] < LIMITS["nodes"], str(gross["nodes"]))
check("Leicht: Szenen werden erst beim Hinscrollen gezeichnet (nicht für alle %d Baustellen)" % SITES, gross["scenes"] < SITES / 2, "%d Szenen" % gross["scenes"])
check("Leicht: die Liste zeigt trotzdem alle Baustellen", gross["sites"] == SITES, str(gross["sites"]))
check("3D: Baustellen sind Teil der Karte, keine Kärtchen mit Szenen auf der Karte (weniger Seitenelemente als Leicht)", d3["nodes"] < gross["nodes"], "%d gegen %d" % (d3["nodes"], gross["nodes"]))
check("Verlauf: lädt höchstens 500 Einträge, zeigt davon nur 40 Zeilen", gross["hist_rows"] == 40, str(gross["hist_rows"]))
check("Verlauf: das offene Fenster hat höchstens 700 Seitenelemente", gross["hist_dom"] < 700, "%d Elemente im Fenster, insgesamt %d zusätzlich" % (gross["hist_dom"], gross["nodes_hist_open"] - gross["nodes_before_hist"]))
check("Verlauf: nach dem Schliessen sind die Seitenelemente wieder wie vorher", gross["dom_after_close"] == gross["dom_before_hist"], "%d vorher, %d nachher" % (gross["dom_before_hist"], gross["dom_after_close"]))
check("Verlauf: nach dem ersten Öffnen bleibt höchstens ein kleiner einmaliger Rest (unter 150 Knoten)", gross["nodes_hist_closed"] - gross["nodes_before_hist"] < 150, "%d Knoten Rest" % (gross["nodes_hist_closed"] - gross["nodes_before_hist"]))
check("Verlauf: wiederholtes Öffnen und Schliessen lässt nichts wachsen (kein Leck)", gross["nodes_hist_closed3"] <= gross["nodes_hist_closed"] + 10, "%d nach 1x, %d nach 3x" % (gross["nodes_hist_closed"], gross["nodes_hist_closed3"]))
bad = [n for n, ok in results if not ok]
print("Ergebnis: %d von %d Pruefungen bestanden" % (len(results) - len(bad), len(results)))
if bad: print("Nicht bestanden:", bad); raise SystemExit(1)
