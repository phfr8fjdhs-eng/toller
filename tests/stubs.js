// Ersatz fuer Supabase und MapLibre, nur fuer Tests
(function(){
  // ---- Audio: die Seite darf nie einen Ton erzeugen (es gibt keinen Alarmton)
  window.__audio = 0;
  window.AudioContext = window.webkitAudioContext = function(){ window.__audio++; };

  // ---- three.js: Ersatz, der nur zaehlt (echtes WebGL wird hier NICHT geprueft, siehe CLAUDE.md)
  const T = window.__three = { renderers:[], rendered:0, disposed:0, contextLost:0, rendererDisposed:0, lastScene:null, texts:[], loads:0, meshes:0 };
  const vec = () => ({ x:0, y:0, z:0, set(x, y, z){ this.x = x; this.y = y; this.z = z; return this; } });
  class Obj {
    constructor(){ this.children = []; this.parent = null; this.userData = {}; this.position = vec(); this.rotation = vec(); this.scale = vec(); this.visible = true; this.holes = []; this.target = vec();
      this.shadow = { mapSize:vec(), camera:{}, bias:0 }; this.shadowMap = {}; }
    add(...c){ c.forEach(x => { x.parent = this; this.children.push(x); }); return this; }
    remove(c){ this.children = this.children.filter(x => x !== c); }
    traverse(f){ f(this); this.children.forEach(c => c.traverse(f)); }
    dispose(){ T.disposed++; this.isDisposed = true; }
    moveTo(){ return this; } lineTo(){ return this; } lookAt(){} updateProjectionMatrix(){} addEventListener(){}
  }
  const special = {
    Mesh: class extends Obj { constructor(g, m){ super(); this.geometry = g; this.material = m; T.meshes++; } },
    WebGLRenderer: class extends Obj {
      constructor(){ super(); if(window.__noWebGL) throw new Error("WebGL nicht verfuegbar"); this.domElement = document.createElement("canvas"); T.renderers.push(this); }
      setPixelRatio(){} setSize(){} setClearColor(){}
      render(scene){ T.rendered++; T.lastScene = scene; }
      dispose(){ T.rendererDisposed++; }
      forceContextLoss(){ T.contextLost++; }
    },
    OrbitControls: class extends Obj { update(){ return false; } }
  };
  window.THREE = new Proxy({}, { get(t, k){
    if(typeof k !== "string") return undefined;
    return special[k] || t[k] || (t[k] = class extends Obj {});
  } });
  // Texte, die auf Zeichenflaechen geschrieben werden (Namensschilder, Bedarfstafel)
  const ft = CanvasRenderingContext2D.prototype.fillText;
  CanvasRenderingContext2D.prototype.fillText = function(t){ T.texts.push(String(t)); return ft.apply(this, arguments); };
  T.machines = () => { const out = []; if(T.lastScene) T.lastScene.traverse(o => { if(o.userData && o.userData.machine !== undefined) out.push(o.userData.machine); }); return out; };

  // ---- MapLibre
  const handlers = {};
  window.__mapHandlers = handlers;
  window.maplibregl = {
    Map: function(){
      Object.keys(handlers).forEach(k => { delete handlers[k]; });     // wie bei MapLibre: alte Karte entfernt, ihre Ereignisse sind weg
      this.addControl = function(){};
      this.on = function(ev, a, b){ const cb = typeof a === "function" ? a : b; (handlers[ev] = handlers[ev] || []).push(cb); if(ev === "load") setTimeout(cb, 150); };
      const data = window.__mapData = {}, layers = window.__mapLayers = {};
      const srcs = window.__mapSrc = {};
      this.addSource = function(id, o){ data[id] = o.data; srcs[id] = o; };
      this.getSource = function(id){ return id in data ? { setData:function(d){ data[id] = d; } } : undefined; };
      this.getStyle = function(){ return { layers:[{ id:"l", type:"symbol", layout:{ "text-font":["Noto Sans Regular"] } }, { id:"background", type:"background" },
        { id:"highway_minor", type:"line" }, { id:"highway_major_casing", type:"line" }, { id:"highway_name_other", type:"symbol", layout:{ "text-field":"{name}" } }],
        sources:{ openmaptiles:{ type:"vector" } } }; };
      const paints = window.__paints = [];
      this.addLayer = function(l){ layers[l.id] = l; }; this.getLayer = function(id){ return layers[id]; };
      this.setPaintProperty = function(id, k, v){ if(layers[id]) layers[id].paint[k] = v; else paints.push([id, k, v]); };
      // Strassennetz der Kartendaten (fuer "Strasse erneuern"), im Test gesetzt
      this.querySourceFeatures = function(src, o){ return o && o.sourceLayer === "transportation" ? (window.__mapRoads || []) : []; };
      this.getCenter = function(){ return { lng:8.85, lat:47.235 }; };
      this.getPitch = function(){ return 55; }; this.getBearing = function(){ return -15; };
      this.queryRenderedFeatures = function(){ return window.__mapHit || []; };
      this.getCanvas = function(){ return document.createElement("canvas"); };
      const images = window.__mapImages = {};
      this.addImage = function(id, img){ images[id] = img; }; this.hasImage = function(id){ return id in images; };
      let terrain = null;
      this.setTerrain = function(o){ terrain = o; }; this.getTerrain = function(){ return terrain; };
      this.easeTo = function(o){ (window.__eases = window.__eases || []).push(o); };
      this.isMoving = function(){ return false; };
      // Hoehe der Kartenmitte gegenueber dem Gelaende (im Test gesetzt, 0 = stimmt)
      this.queryTerrainElevation = function(){ return terrain ? (window.__terrainDiff || 0) : null; };
      this.fitBounds = function(){ window.__fits = (window.__fits || 0) + 1; };
      this.flyTo = function(o){ window.__fly = o.center.join(","); };
      this.getZoom = function(){ return 12; };
      this.remove = function(){};
    },
    NavigationControl: function(){},
    Popup: function(o){
      const self = this; let node = null;
      this.setLngLat = function(p){ self.pos = p; return self; };
      this.setDOMContent = function(n){ node = n; const box = document.getElementById("stubPopup"); if(box){ box.innerHTML = ""; box.appendChild(n); } return self; };
      this.addTo = function(){ let box = document.getElementById("stubPopup"); if(!box){ box = document.createElement("div"); box.id = "stubPopup"; document.getElementById("lmap").appendChild(box); }
        box.innerHTML = ""; if(node) box.appendChild(node); window.__popup = self; return self; };
      this.remove = function(){ const box = document.getElementById("stubPopup"); if(box) box.remove(); if(window.__popup === self) window.__popup = null; };
      this.on = function(){ return self; };
    },
    LngLatBounds: function(){ this.extend = function(){ return this; }; },
    Marker: function(o){
      const el = o.element;
      this.setLngLat = function(){ return this; };
      this.addTo = function(){ document.getElementById("lmap").appendChild(el); return this; };
      this.getElement = function(){ return el; };
      this.remove = function(){ el.remove(); };
    }
  };
  window.__mapClick = function(lat, lng){ (handlers.click || []).forEach(cb => cb({ lngLat:{ lat, lng } })); };
  // Klick auf eine Baustelle der Karte (Fläche oder Punkt)
  window.__mapClickFeature = function(props){ window.__mapHit = [{ properties:props }]; (handlers.click || []).forEach(cb => cb({ lngLat:{ lat:0, lng:0 }, point:{ x:1, y:1 } })); window.__mapHit = []; };
  window.__mapClickSite = function(id){ window.__mapHit = [{ properties:{ id } }]; (handlers.click || []).forEach(cb => cb({ lngLat:{ lat:0, lng:0 }, point:{ x:1, y:1 } })); window.__mapHit = []; };
  // Baustellen, wie die Karte sie gerade zeigt
  window.__mapSites = function(){ const d = window.__mapData && window.__mapData["site-pts"]; return d ? d.features.map(f => f.properties) : []; };

  // ---- Supabase
  const db = window.__db = { sites:[], machines:[], needs:[], materials:[], activity:[], downtimes:[], drawings:[], profiles:[], users:{}, session:null, handlers:[], authCbs:[], seq:1, autoConfirm:true, failNext:null, resets:[], failReset:null };
  const nid = () => "id" + (db.seq++);
  const me = () => db.session ? db.profiles.find(p => p.id === db.session.user.id) : null;
  const approved = () => { const m = me(); return !!(m && m.approved); };
  const admin = () => { const m = me(); return !!(m && m.approved && m.role === "admin"); };
  function emit(table, type, nw, old){
    db.handlers.filter(h => h.table === table && (h.event === "*" || h.event === type))
      .forEach(h => h.cb({ eventType:type, new:nw || {}, old:old || {} }));
  }
  db.emit = emit;

  // Wie der Trigger machines_stamp: Absender und Zeit setzt die Datenbank, nie die Seite
  function stamp(r, old){
    if(old && r.status === old.status && r.reason === old.reason){ r.reported_by = old.reported_by; r.reported_name = old.reported_name; r.reported_at = old.reported_at; return; }
    if(r.status === "waiting" || r.status === "broken"){ r.reported_by = (me() || {}).id; r.reported_name = (me() || {}).name || ""; r.reported_at = new Date().toISOString(); }
    else { r.reported_by = null; r.reported_name = ""; r.reported_at = null; }
  }

  // Wie der Trigger downtimes_track: die Datenbank schreibt den Verlauf der Stoerungen, nie die Seite
  function track(nw, old, op){
    const id = (nw || old).id, bad = x => x === "waiting" || x === "broken";
    const open = () => db.downtimes.find(d => d.machine_id === id && !d.ended_at);
    if(op === "delete"){ const o = open(); if(o) o.ended_at = new Date().toISOString(); db.downtimes.forEach(d => { if(d.machine_id === id) d.machine_id = null; }); return; }
    if(op === "update"){
      if(nw.status === old.status && nw.reason === old.reason) return;
      if(bad(nw.status) && nw.status === old.status && String(nw.reason).split(" · ")[0] === String(old.reason).split(" · ")[0]){ const o = open(); if(o) o.reason = nw.reason; return; }
    }
    const o = open(); if(o) o.ended_at = new Date().toISOString();
    if(bad(nw.status)){
      const site = db.sites.find(x => x.id === nw.site_id);
      db.downtimes.push({ id:db.seq++, machine_id:nw.id, machine_name:nw.name, typ:nw.typ || "", site_name:site ? site.name : "", kind:nw.status, reason:nw.reason || "", reported_name:nw.reported_name || "", started_at:new Date().toISOString(), ended_at:null });
    }
  }

  function Q(t){ this.t = t; this.op = "select"; this.fl = []; this.row = null; this.one = false; this.maybe = false; this.sel = false; this.ord = null; this.lim = null; }
  Q.prototype = {
    select(cols){ this.sel = true; this.cols = cols || "*"; return this; },
    insert(r){ this.op = "insert"; this.row = r; return this; },
    update(r){ this.op = "update"; this.row = r; return this; },
    delete(){ this.op = "delete"; return this; },
    eq(k, v){ this.fl.push(r => r[k] === v); return this; },
    gte(k, v){ this.fl.push(r => r[k] >= v); return this; },
    like(k, p){ const pre = p.replace("%", ""); this.fl.push(r => String(r[k]).indexOf(pre) === 0); return this; },
    order(k, o){ this.ord = [k, !(o && o.ascending === false)]; return this; },
    limit(n){ this.lim = n; return this; },
    single(){ this.one = true; return this; },
    maybeSingle(){ this.maybe = true; return this; },
    then(res, rej){ return Promise.resolve().then(() => this.run()).then(res, rej); },
    run(){
      if(db.failNext && db.failNext.table === this.t){ const e = db.failNext.msg; db.failNext = null; return { data:null, error:{ message:e } }; }
      // Alte Datenbank ohne Spalte weitere_sparten (schema.sql noch nicht erneut ausgefuehrt)
      if(db.noSpartenCol && this.t === "sites"){
        const colErr = { data:null, error:{ code:"42703", message:"column sites.weitere_sparten does not exist" } };
        if(this.op === "select" && /weitere_sparten/.test(this.cols || "")) return colErr;
        if((this.op === "insert" || this.op === "update") && this.row && "weitere_sparten" in this.row) return colErr;
      }
      const T = db[this.t];
      if(!T) return { data:null, error:{ code:"42P01", message:"relation \"public." + this.t + "\" does not exist" } };   // Tabelle fehlt (altes schema.sql)
      const isProf = this.t === "profiles";
      const canRead = isProf ? (r => admin() || (me() && r.id === me().id)) : (() => approved());
      const rls = { message:"new row violates row-level security policy" };
      if(this.t === "downtimes" && this.op !== "select") return { data:null, error:{ message:"permission denied for table downtimes" } };   // nur der Trigger schreibt
      let rows = T.filter(r => canRead(r) && this.fl.every(f => f(r)));
      if(this.op === "insert"){
        if(isProf || !approved()) return { data:null, error:rls };
        const made = [];
        for(const src of (Array.isArray(this.row) ? this.row : [this.row])){       // eine Zeile oder mehrere auf einmal
          const row = Object.assign({ id:this.t === "activity" ? db.seq++ : nid(), created_at:new Date().toISOString() }, this.t === "machines" ? { typ:"", status:"off", reason:"", site_id:null } : {}, this.t === "needs" ? { author:"", done:false, done_by:"", done_at:null, created_by:(me() || {}).id } : {}, src);
          if(this.t === "materials"){                                         // wie der Trigger materials_stamp und der eindeutige Index
            row.name = String(row.name || "").replace(/\s+/g, " ").trim();
            row.author = me().name; row.created_by = me().id;
            if(row.name.length < 2 || row.name.length > 60) return { data:null, error:{ message:"violates check constraint" } };
            if(T.some(x => x.name.toLowerCase() === row.name.toLowerCase())) return { data:null, error:{ code:"23505", message:"duplicate key value violates unique constraint" } };
          }
          if(this.t === "machines") stamp(row, null);
          if(this.t === "drawings"){                                          // wie der Trigger drawings_stamp und die Pruefung
            row.author = me().name; row.created_by = me().id;
            const ok = { baum:"Point", strasse:"LineString", wasser:"LineString", abwasser:"LineString", gas:"LineString", strom:"LineString", kabel:"LineString", hecke:"LineString", bereich:"Polygon", rasen:"Polygon", belag:"Polygon" }[row.kind];
            if(!row.geom || row.geom.type !== ok) return { data:null, error:{ message:"new row violates check constraint drawings_geom_ok" } };
          }
          made.push(row);
        }
        made.forEach(row => { T.push(row); if(this.t === "machines") track(row, null, "insert"); emit(this.t, "INSERT", row); });
        return this.sel ? { data:this.one ? made[0] : made, error:null } : { data:null, error:null };
      }
      if(this.op === "update"){
        if(isProf ? !admin() : !approved()) return { data:[], error:null };
        if(this.t === "materials") return { data:[], error:null };           // Materialien lassen sich nicht aendern
        if(this.t === "drawings") return { data:null, error:{ message:"permission denied for table drawings" } };   // nie aendern
        rows.forEach(r => { const old = Object.assign({}, r); Object.assign(r, this.row); if(this.t === "machines"){ stamp(r, old); track(r, old, "update"); } emit(this.t, "UPDATE", r, old); });
        if(this.one) return rows.length === 1 ? { data:rows[0], error:null } : { data:null, error:{ message:"JSON object requested, multiple (or no) rows returned" } };
        return { data:rows, error:null };
      }
      if(this.op === "delete"){
        if(this.t === "needs" || this.t === "materials" || this.t === "drawings") rows = rows.filter(r => admin() || r.created_by === (me() || {}).id);   // Schreiber oder Admin
        else if(!admin()) return { data:[], error:null };
        rows.forEach(r => { if(this.t === "machines") track(null, r, "delete"); T.splice(T.indexOf(r), 1); emit(this.t, "DELETE", null, { id:r.id }); });
        return { data:rows, error:null };
      }
      if(this.ord) rows = rows.slice().sort((a, b) => (a[this.ord[0]] > b[this.ord[0]] ? 1 : -1) * (this.ord[1] ? 1 : -1));
      if(this.lim) rows = rows.slice(0, this.lim);
      rows = rows.map(r => Object.assign({}, r));
      if(this.one || this.maybe) return { data:rows[0] || null, error:(this.one && !rows[0]) ? { message:"not found" } : null };
      return { data:rows, error:null };
    }
  };

  function setSession(user){
    db.session = user ? { user:{ id:user.id, email:user.email } } : null;
    db.authCbs.forEach(cb => cb(user ? "SIGNED_IN" : "SIGNED_OUT", db.session));
  }
  db.signInAs = email => { const u = db.users[email]; setSession(u); };
  // Wie nach dem Klick auf den Link in der Mail: angemeldet, dann das Ereignis PASSWORD_RECOVERY
  db.recoverAs = email => { setSession(db.users[email]); db.authCbs.forEach(cb => cb("PASSWORD_RECOVERY", db.session)); };

  window.supabase = {
    createClient(){
      return {
        auth:{
          async getSession(){ return { data:{ session:db.session } }; },
          onAuthStateChange(cb){ db.authCbs.push(cb); return { data:{ subscription:{} } }; },
          async signUp(o){
            if(db.users[o.email]) return { data:{}, error:{ message:"User already registered" } };
            const u = { id:nid(), email:o.email, password:o.password };
            db.users[o.email] = u;
            const first = db.profiles.length === 0;
            db.profiles.push({ id:u.id, email:o.email, name:(o.options && o.options.data && o.options.data.name) || o.email.split("@")[0], role:first ? "admin" : "mitarbeiter", approved:first, created_at:new Date().toISOString() });
            if(db.autoConfirm){ setSession(u); return { data:{ session:db.session }, error:null }; }
            return { data:{ session:null }, error:null };
          },
          async signInWithPassword(o){
            const u = db.users[o.email];
            if(!u || u.password !== o.password) return { data:{}, error:{ message:"Invalid login credentials" } };
            setSession(u); return { data:{ session:db.session }, error:null };
          },
          async signOut(){ setSession(null); return { error:null }; },
          // Passwort vergessen: wie Supabase immer ohne Fehler, auch wenn es die Adresse nicht gibt
          async resetPasswordForEmail(email, o){
            db.resets.push({ email, redirectTo:o && o.redirectTo });
            return db.failReset ? { data:null, error:db.failReset } : { data:{}, error:null };
          },
          async updateUser(o){
            if(!db.session) return { data:null, error:{ message:"Auth session missing!" } };
            const u = Object.values(db.users).find(x => x.id === db.session.user.id);
            if(u.password === o.password) return { data:null, error:{ message:"New password should be different from the old password." } };
            u.password = o.password; db.passwordChanges = (db.passwordChanges || 0) + 1;
            return { data:{ user:{ id:u.id } }, error:null };
          }
        },
        from(t){ return new Q(t); },
        channel(){
          const ch = { on(type, f, cb){ db.handlers.push({ table:f.table, event:f.event, cb }); return ch; },
                       subscribe(cb){ setTimeout(() => cb("SUBSCRIBED"), 0); return ch; } };
          return ch;
        },
        removeChannel(){ db.handlers.length = 0; }
      };
    }
  };
})();
