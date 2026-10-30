// Ersatz fuer Supabase und MapLibre, nur fuer Tests
(function(){
  // ---- Audio: die Seite darf nie einen Ton erzeugen (es gibt keinen Alarmton)
  window.__audio = 0;
  window.AudioContext = window.webkitAudioContext = function(){ window.__audio++; };

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
  const db = window.__db = { sites:[], machines:[], activity:[], profiles:[], users:{}, session:null, handlers:[], authCbs:[], seq:1, autoConfirm:true, failNext:null };
  const nid = () => "id" + (db.seq++);
  const me = () => db.session ? db.profiles.find(p => p.id === db.session.user.id) : null;
  const approved = () => { const m = me(); return !!(m && m.approved); };
  const admin = () => { const m = me(); return !!(m && m.approved && m.role === "admin"); };
  function emit(table, type, nw, old){
    db.handlers.filter(h => h.table === table && (h.event === "*" || h.event === type))
      .forEach(h => h.cb({ eventType:type, new:nw || {}, old:old || {} }));
  }
  db.emit = emit;

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
        const row = Object.assign({ id:this.t === "activity" ? db.seq++ : nid(), created_at:new Date().toISOString() }, this.t === "machines" ? { typ:"", status:"off", reason:"", site_id:null } : {}, this.row);
        T.push(row); emit(this.t, "INSERT", row);
        return this.sel ? { data:this.one ? row : [row], error:null } : { data:null, error:null };
      }
      if(this.op === "update"){
        if(isProf ? !admin() : !approved()) return { data:[], error:null };
        rows.forEach(r => { const old = Object.assign({}, r); Object.assign(r, this.row); emit(this.t, "UPDATE", r, old); });
        return { data:rows, error:null };
      }
      if(this.op === "delete"){
        if(!admin()) return { data:[], error:null };
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
