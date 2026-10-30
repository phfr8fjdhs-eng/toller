// Ersatz fuer Supabase und MapLibre, nur fuer Tests
(function(){
  // ---- Audio: die Seite darf nie einen Ton erzeugen (es gibt keinen Alarmton)
  window.__audio = 0;
  window.AudioContext = window.webkitAudioContext = function(){ window.__audio++; };

  // ---- three.js: Ersatz, der nur zaehlt (echtes WebGL wird hier NICHT geprueft, siehe CLAUDE.md)
  const T = window.__three = { renderers:[], rendered:0, disposed:0, contextLost:0, rendererDisposed:0, lastScene:null, texts:[], loads:0, meshes:0 };
  const vec = () => ({ x:0, y:0, z:0, set(x, y, z){ this.x = x; this.y = y; this.z = z; return this; } });
  class Obj {
    constructor(){ this.children = []; this.parent = null; this.userData = {}; this.position = vec(); this.rotation = vec(); this.scale = vec(); this.visible = true; this.holes = []; this.target = vec(); }
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
      this.addControl = function(){};
      this.on = function(ev, cb){ (handlers[ev] = handlers[ev] || []).push(cb); if(ev === "load") setTimeout(cb, 150); };
      this.addSource = function(){}; this.getStyle = function(){ return { layers:[{ id:"l", type:"symbol" }] }; };
      this.addLayer = function(){}; this.setTerrain = function(){}; this.easeTo = function(){};
      this.fitBounds = function(){ window.__fits = (window.__fits || 0) + 1; };
      this.flyTo = function(o){ window.__fly = o.center.join(","); };
      this.getZoom = function(){ return 12; };
      this.remove = function(){};
    },
    NavigationControl: function(){},
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

  // ---- Supabase
  const db = window.__db = { sites:[], machines:[], needs:[], materials:[], activity:[], profiles:[], users:{}, session:null, handlers:[], authCbs:[], seq:1, autoConfirm:true, failNext:null };
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

  function Q(t){ this.t = t; this.op = "select"; this.fl = []; this.row = null; this.one = false; this.maybe = false; this.sel = false; this.ord = null; this.lim = null; }
  Q.prototype = {
    select(){ this.sel = true; return this; },
    insert(r){ this.op = "insert"; this.row = r; return this; },
    update(r){ this.op = "update"; this.row = r; return this; },
    delete(){ this.op = "delete"; return this; },
    eq(k, v){ this.fl.push(r => r[k] === v); return this; },
    like(k, p){ const pre = p.replace("%", ""); this.fl.push(r => String(r[k]).indexOf(pre) === 0); return this; },
    order(k, o){ this.ord = [k, !(o && o.ascending === false)]; return this; },
    limit(n){ this.lim = n; return this; },
    single(){ this.one = true; return this; },
    maybeSingle(){ this.maybe = true; return this; },
    then(res, rej){ return Promise.resolve().then(() => this.run()).then(res, rej); },
    run(){
      if(db.failNext && db.failNext.table === this.t){ const e = db.failNext.msg; db.failNext = null; return { data:null, error:{ message:e } }; }
      const T = db[this.t];
      const isProf = this.t === "profiles";
      const canRead = isProf ? (r => admin() || (me() && r.id === me().id)) : (() => approved());
      const rls = { message:"new row violates row-level security policy" };
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
          made.push(row);
        }
        made.forEach(row => { T.push(row); emit(this.t, "INSERT", row); });
        return this.sel ? { data:this.one ? made[0] : made, error:null } : { data:null, error:null };
      }
      if(this.op === "update"){
        if(isProf ? !admin() : !approved()) return { data:[], error:null };
        if(this.t === "materials") return { data:[], error:null };           // Materialien lassen sich nicht aendern
        rows.forEach(r => { const old = Object.assign({}, r); Object.assign(r, this.row); if(this.t === "machines") stamp(r, old); emit(this.t, "UPDATE", r, old); });
        return { data:rows, error:null };
      }
      if(this.op === "delete"){
        if(this.t === "needs" || this.t === "materials") rows = rows.filter(r => admin() || r.created_by === (me() || {}).id);   // Schreiber oder Admin
        else if(!admin()) return { data:[], error:null };
        rows.forEach(r => { T.splice(T.indexOf(r), 1); emit(this.t, "DELETE", null, { id:r.id }); });
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
          async signOut(){ setSession(null); return { error:null }; }
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
