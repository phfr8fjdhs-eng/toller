-- Baustellen-Dashboard: Datenbank
-- Einmal im Supabase "SQL Editor" ausführen (Anleitung: SUPABASE-ANLEITUNG.md).
--
-- Sicherheit:
--  * Wer sich registriert, sieht zuerst NICHTS, bis ein Admin die Person freigibt.
--  * Die allererste Person, die sich registriert, wird automatisch Admin.
--    Registriere dich deshalb sofort nach der Einrichtung selbst.
--  * Freigegebene Mitarbeiter dürfen Baustellen und Maschinen ansehen, anlegen und ändern.
--  * Bedarf (was auf einer Baustelle gebraucht wird): Freigegebene schreiben und haken ab,
--    löschen dürfen der Schreiber selbst und Admins.
--  * Meldungen an Maschinen (Defekt, Material fehlt, Diesel fehlt): Name der meldenden Person und Zeit
--    trägt die Datenbank selbst ein, die Seite kann das nicht fälschen.
--  * Materialien: der grosse Katalog steckt in der Seite (public/materialien.js). Eigene Einträge von
--    Mitarbeitern stehen in der Tabelle materials und gelten für alle. Freigegebene schreiben, löschen
--    darf der Schreiber selbst und Admins.
--  * Zeichnungen auf der Karte (Strassen, Leitungen, Bäume, Flächen): Freigegebene lesen und zeichnen,
--    löschen darf der Zeichner selbst und Admins. Nur eine Skizze, keine Vermessung.
--  * Löschen von Baustellen und Maschinen und Benutzer verwalten darf nur ein Admin.
--
-- Update einer bestehenden Datenbank: diese Datei einfach nochmals ausführen (sie ist wiederholbar).

-- ---------------------------------------------------------------- Tabellen

create table if not exists public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  email       text,
  name        text,
  role        text not null default 'mitarbeiter' check (role in ('admin', 'mitarbeiter')),
  approved    boolean not null default false,
  created_at  timestamptz not null default now()
);

create table if not exists public.sites (
  id              uuid primary key default gen_random_uuid(),
  name            text not null check (length(trim(name)) > 0),
  sparte          text not null check (sparte in ('garten', 'strasse', 'tief')),
  lat             double precision not null check (lat between -90 and 90),
  lng             double precision not null check (lng between -180 and 180),
  created_by      uuid default auth.uid(),
  created_at      timestamptz not null default now()
);

create table if not exists public.machines (
  id          uuid primary key default gen_random_uuid(),
  name        text not null check (length(trim(name)) > 0),
  typ         text not null default '',
  sparte      text not null check (sparte in ('garten', 'strasse', 'tief')),
  site_id     uuid references public.sites(id) on delete set null,
  status      text not null default 'off' check (status in ('running', 'waiting', 'broken', 'off')),
  reason      text not null default '',
  created_by  uuid default auth.uid(),
  updated_at  timestamptz not null default now()
);
-- Weitere Sparten einer Baustelle (zusätzlich zur Hauptsparte), z. B. Strassenbau + Tiefbau zusammen.
-- Die Hauptsparte steht weiter in "sparte". Der Trigger sites_sparten entfernt Doppelte und die Hauptsparte.
alter table public.sites add column if not exists weitere_sparten text[] not null default '{}';
alter table public.sites drop constraint if exists sites_weitere_sparten_check;
alter table public.sites add constraint sites_weitere_sparten_check
  check (weitere_sparten <@ array['garten', 'strasse', 'tief']::text[] and cardinality(weitere_sparten) <= 2);

-- Wer hat die Meldung abgeschickt (Defekt, wartet): setzt der Trigger machines_stamp, nicht die Seite
alter table public.machines add column if not exists reported_by   uuid;
alter table public.machines add column if not exists reported_name text not null default '';
alter table public.machines add column if not exists reported_at   timestamptz;

-- Bedarf je Baustelle: freier Text, zum Beispiel "20 m³ Beton bis Mittwoch"
create table if not exists public.needs (
  id          uuid primary key default gen_random_uuid(),
  site_id     uuid not null references public.sites(id) on delete cascade,
  text        text not null check (length(trim(text)) between 1 and 200),
  author      text not null default '' check (length(author) <= 60),
  created_by  uuid not null default auth.uid(),
  created_at  timestamptz not null default now(),
  done        boolean not null default false,
  done_by     text not null default '' check (length(done_by) <= 60),
  done_at     timestamptz
);

create table if not exists public.activity (
  id          bigint generated always as identity primary key,
  created_at  timestamptz not null default now(),
  user_id     uuid default auth.uid(),
  text        text not null check (length(text) between 1 and 300)
);

-- Eigene Materialien der Mitarbeiter (zusätzlich zum Katalog in der Seite), gelten für alle
create table if not exists public.materials (
  id          uuid primary key default gen_random_uuid(),
  name        text not null check (length(trim(name)) between 2 and 60),
  author      text not null default '' check (length(author) <= 60),
  created_by  uuid not null default auth.uid(),
  created_at  timestamptz not null default now()
);
create unique index if not exists materials_name_uniq on public.materials (lower(trim(name)));

create index if not exists machines_site_idx on public.machines(site_id);
create index if not exists needs_site_idx on public.needs(site_id);
create index if not exists activity_created_idx on public.activity(created_at desc);

-- Zeichnungen auf der Karte je Baustelle: Linien (Strasse, Strasse erneuern, Leitungen, Hecke), Punkte (Baum), Flächen.
-- geom ist eine GeoJSON-Geometrie [Längengrad, Breitengrad]. Nur eine Skizze zur Übersicht, keine Vermessung:
-- gezeichnete Leitungen ersetzen keinen Werkleitungsplan.
create table if not exists public.drawings (
  id          uuid primary key default gen_random_uuid(),
  site_id     uuid not null references public.sites(id) on delete cascade,
  kind        text not null,
  geom        jsonb not null,
  label       text not null default '' check (length(label) <= 60),
  author      text not null default '' check (length(author) <= 60),
  created_by  uuid not null default auth.uid(),
  created_at  timestamptz not null default now()
);
create index if not exists drawings_site_idx on public.drawings(site_id);
-- Welche Seite einer Linie betroffen ist (z. B. nur eine Strassenseite): links/rechts in Zeichnungsrichtung
alter table public.drawings add column if not exists seite text not null default 'beide';
alter table public.drawings drop constraint if exists drawings_seite_check;
alter table public.drawings add constraint drawings_seite_check check (seite in ('beide', 'links', 'rechts'));

-- ---------------------------------------------------------------- Hilfsfunktionen

create or replace function public.is_approved()
returns boolean
language sql security definer stable
set search_path = public
as $$
  select exists (select 1 from public.profiles where id = auth.uid() and approved);
$$;

-- Eine Position [Längengrad, Breitengrad] als Zahlen im gültigen Bereich (CASE prüft der Reihe nach, nie ein Fehler)
create or replace function public.drawing_pos_ok(p jsonb)
returns boolean
language sql immutable
set search_path = public
as $$
  select case
    when p is null or jsonb_typeof(p) <> 'array' then false
    when jsonb_array_length(p) <> 2 then false
    when jsonb_typeof(p->0) <> 'number' or jsonb_typeof(p->1) <> 'number' then false
    else (p->>0)::float8 between -180 and 180 and (p->>1)::float8 between -90 and 90
  end;
$$;

-- Passt die Geometrie zur Art? Baum = Punkt, Linien = 2 bis 500 Punkte, Flächen = ein geschlossener Ring mit 3 bis 500 Ecken
create or replace function public.drawing_ok(k text, g jsonb)
returns boolean
language plpgsql immutable
set search_path = public
as $$
declare
  t text;
  c jsonb;
  ring jsonb;
  p jsonb;
  n int;
begin
  if g is null or jsonb_typeof(g) <> 'object' then return false; end if;
  if octet_length(g::text) > 40000 then return false; end if;
  t := g->>'type';
  c := g->'coordinates';
  if c is null or jsonb_typeof(c) <> 'array' then return false; end if;
  if k = 'baum' then
    return t = 'Point' and public.drawing_pos_ok(c);
  elsif k in ('strasse', 'erneuern', 'wasser', 'abwasser', 'gas', 'strom', 'kabel', 'hecke') then
    if t is distinct from 'LineString' then return false; end if;
    n := jsonb_array_length(c);
    if n < 2 or n > 500 then return false; end if;
    for p in select value from jsonb_array_elements(c) loop
      if not public.drawing_pos_ok(p) then return false; end if;
    end loop;
    return true;
  elsif k in ('bereich', 'rasen', 'belag') then
    if t is distinct from 'Polygon' or jsonb_array_length(c) <> 1 then return false; end if;
    ring := c->0;
    if jsonb_typeof(ring) <> 'array' then return false; end if;
    n := jsonb_array_length(ring);
    if n < 4 or n > 501 then return false; end if;
    if ring->0 is distinct from ring->(n - 1) then return false; end if;
    for p in select value from jsonb_array_elements(ring) loop
      if not public.drawing_pos_ok(p) then return false; end if;
    end loop;
    return true;
  end if;
  return false;
end;
$$;

create or replace function public.is_admin()
returns boolean
language sql security definer stable
set search_path = public
as $$
  select exists (select 1 from public.profiles where id = auth.uid() and approved and role = 'admin');
$$;

-- Neues Profil bei jeder Registrierung. Die erste Person wird freigegebener Admin.
create or replace function public.handle_new_user()
returns trigger
language plpgsql security definer
set search_path = public
as $$
declare
  first_user boolean;
begin
  select not exists (select 1 from public.profiles) into first_user;
  insert into public.profiles (id, email, name, role, approved)
  values (
    new.id,
    new.email,
    coalesce(nullif(new.raw_user_meta_data ->> 'name', ''), split_part(new.email, '@', 1)),
    case when first_user then 'admin' else 'mitarbeiter' end,
    first_user
  );
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- Beim Bedarf dürfen Mitarbeiter nur abhaken (done, done_by, done_at). Der Inhalt ändert nur ein Admin.
create or replace function public.needs_guard()
returns trigger
language plpgsql
as $$
begin
  if not public.is_admin() and (
       new.text       is distinct from old.text
    or new.site_id    is distinct from old.site_id
    or new.author     is distinct from old.author
    or new.created_by is distinct from old.created_by
    or new.created_at is distinct from old.created_at
  ) then
    raise exception 'Der Inhalt eines Bedarfs kann nur von Admins geändert werden';
  end if;
  return new;
end;
$$;

drop trigger if exists needs_guard_trg on public.needs;
create trigger needs_guard_trg
  before update on public.needs
  for each row execute function public.needs_guard();

-- Weitere Sparten ordnen: ohne Doppelte, ohne die Hauptsparte, feste Reihenfolge (garten, strasse, tief).
-- Unbekannte Werte bleiben stehen, damit die Prüfung sie ablehnt (nichts wird still verschluckt).
create or replace function public.sites_sparten()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  new.weitere_sparten := coalesce(array(
    select x from (select distinct x from unnest(coalesce(new.weitere_sparten, '{}'::text[])) as u(x)
                   where x is distinct from new.sparte) d
    order by coalesce(array_position(array['garten', 'strasse', 'tief']::text[], x), 99), x
  ), '{}'::text[]);
  return new;
end;
$$;

drop trigger if exists sites_sparten_trg on public.sites;
create trigger sites_sparten_trg
  before insert or update on public.sites
  for each row execute function public.sites_sparten();

-- Zeichnungen: Art und Geometrie werden geprüft, Name des Zeichners setzt die Datenbank
alter table public.drawings drop constraint if exists drawings_geom_ok;
alter table public.drawings add constraint drawings_geom_ok check (public.drawing_ok(kind, geom));

create or replace function public.drawings_stamp()
returns trigger
language plpgsql security definer
set search_path = public
as $$
declare
  who text;
begin
  new.label := left(regexp_replace(trim(coalesce(new.label, '')), '\s+', ' ', 'g'), 60);
  select coalesce(nullif(trim(name), ''), email, '') into who from public.profiles where id = auth.uid();
  new.author := left(coalesce(who, ''), 60);
  return new;
end;
$$;

drop trigger if exists drawings_stamp_trg on public.drawings;
create trigger drawings_stamp_trg
  before insert on public.drawings
  for each row execute function public.drawings_stamp();

-- Absender und Zeit einer Meldung setzt die Datenbank, nie die Seite.
-- Neue Meldung (Status oder Grund ändert sich auf wartet/defekt): aktuelle Person und Zeit.
-- Läuft die Maschine wieder oder ist sie im Werkhof: gelöscht. Sonst bleibt alles, wie es war.
create or replace function public.machines_stamp()
returns trigger
language plpgsql security definer
set search_path = public
as $$
declare
  who text;
  changed boolean := true;
begin
  if tg_op = 'UPDATE' then
    changed := new.status is distinct from old.status or new.reason is distinct from old.reason;
    if not changed then
      new.reported_by := old.reported_by; new.reported_name := old.reported_name; new.reported_at := old.reported_at;
      return new;
    end if;
  end if;
  if new.status in ('waiting', 'broken') then
    select coalesce(nullif(trim(name), ''), email, '') into who from public.profiles where id = auth.uid();
    new.reported_by := auth.uid();
    new.reported_name := left(coalesce(who, ''), 60);
    new.reported_at := now();
  else
    new.reported_by := null; new.reported_name := ''; new.reported_at := null;
  end if;
  return new;
end;
$$;

drop trigger if exists machines_stamp_trg on public.machines;
create trigger machines_stamp_trg
  before insert or update on public.machines
  for each row execute function public.machines_stamp();

-- Eigene Materialien: Name der schreibenden Person setzt die Datenbank, Leerzeichen werden bereinigt
create or replace function public.materials_stamp()
returns trigger
language plpgsql security definer
set search_path = public
as $$
declare
  who text;
begin
  new.name := regexp_replace(trim(new.name), '\s+', ' ', 'g');
  select coalesce(nullif(trim(name), ''), email, '') into who from public.profiles where id = auth.uid();
  new.author := left(coalesce(who, ''), 60);
  return new;
end;
$$;

drop trigger if exists materials_stamp_trg on public.materials;
create trigger materials_stamp_trg
  before insert on public.materials
  for each row execute function public.materials_stamp();

drop trigger if exists machines_touch on public.machines;
create trigger machines_touch
  before update on public.machines
  for each row execute function public.touch_updated_at();

-- ---------------------------------------------------------------- Zugriffsregeln (Row Level Security)

alter table public.profiles enable row level security;
alter table public.sites    enable row level security;
alter table public.machines enable row level security;
alter table public.needs    enable row level security;
alter table public.materials enable row level security;
alter table public.activity enable row level security;
alter table public.drawings enable row level security;

-- Profile: jeder sieht das eigene, Admins sehen alle und verwalten sie
drop policy if exists profiles_select on public.profiles;
create policy profiles_select on public.profiles
  for select to authenticated
  using (id = auth.uid() or public.is_admin());

drop policy if exists profiles_update on public.profiles;
create policy profiles_update on public.profiles
  for update to authenticated
  using (public.is_admin())
  with check (public.is_admin());

drop policy if exists profiles_delete on public.profiles;
create policy profiles_delete on public.profiles
  for delete to authenticated
  using (public.is_admin() and id <> auth.uid());

-- Baustellen
drop policy if exists sites_select on public.sites;
create policy sites_select on public.sites
  for select to authenticated using (public.is_approved());

drop policy if exists sites_insert on public.sites;
create policy sites_insert on public.sites
  for insert to authenticated with check (public.is_approved());

drop policy if exists sites_update on public.sites;
create policy sites_update on public.sites
  for update to authenticated using (public.is_approved()) with check (public.is_approved());

drop policy if exists sites_delete on public.sites;
create policy sites_delete on public.sites
  for delete to authenticated using (public.is_admin());

-- Maschinen
drop policy if exists machines_select on public.machines;
create policy machines_select on public.machines
  for select to authenticated using (public.is_approved());

drop policy if exists machines_insert on public.machines;
create policy machines_insert on public.machines
  for insert to authenticated with check (public.is_approved());

drop policy if exists machines_update on public.machines;
create policy machines_update on public.machines
  for update to authenticated using (public.is_approved()) with check (public.is_approved());

drop policy if exists machines_delete on public.machines;
create policy machines_delete on public.machines
  for delete to authenticated using (public.is_admin());

-- Bedarf: Freigegebene lesen, schreiben (nur als sich selbst) und haken ab.
-- Löschen darf der Schreiber selbst oder ein Admin.
drop policy if exists needs_select on public.needs;
create policy needs_select on public.needs
  for select to authenticated using (public.is_approved());

drop policy if exists needs_insert on public.needs;
create policy needs_insert on public.needs
  for insert to authenticated with check (public.is_approved() and created_by = auth.uid());

drop policy if exists needs_update on public.needs;
create policy needs_update on public.needs
  for update to authenticated using (public.is_approved()) with check (public.is_approved());

drop policy if exists needs_delete on public.needs;
create policy needs_delete on public.needs
  for delete to authenticated using (public.is_admin() or (public.is_approved() and created_by = auth.uid()));

-- Materialien (eigene Einträge): Freigegebene lesen und schreiben (nur als sich selbst), nichts ändern.
-- Löschen darf der Schreiber selbst oder ein Admin.
drop policy if exists materials_select on public.materials;
create policy materials_select on public.materials
  for select to authenticated using (public.is_approved());

drop policy if exists materials_insert on public.materials;
create policy materials_insert on public.materials
  for insert to authenticated with check (public.is_approved() and created_by = auth.uid());

drop policy if exists materials_delete on public.materials;
create policy materials_delete on public.materials
  for delete to authenticated using (public.is_admin() or (public.is_approved() and created_by = auth.uid()));

-- Protokoll: lesen und ergänzen, nicht ändern
drop policy if exists activity_select on public.activity;
create policy activity_select on public.activity
  for select to authenticated using (public.is_approved());

drop policy if exists activity_insert on public.activity;
create policy activity_insert on public.activity
  for insert to authenticated with check (public.is_approved());

-- Zeichnungen: Freigegebene lesen und zeichnen (nur als sich selbst), nichts ändern.
-- Löschen darf der Zeichner selbst oder ein Admin.
drop policy if exists drawings_select on public.drawings;
create policy drawings_select on public.drawings
  for select to authenticated using (public.is_approved());

drop policy if exists drawings_insert on public.drawings;
create policy drawings_insert on public.drawings
  for insert to authenticated with check (public.is_approved() and created_by = auth.uid());

drop policy if exists drawings_delete on public.drawings;
create policy drawings_delete on public.drawings
  for delete to authenticated using (public.is_admin() or (public.is_approved() and created_by = auth.uid()));

-- ---------------------------------------------------------------- Störungsverlauf
-- Jede Störung (Defekt) und jede Wartezeit (Material oder Diesel fehlt) wird von der Datenbank mitgeschrieben:
-- Beginn = Meldung, Ende = "Repariert", "Nachgeliefert", "Getankt" oder Maschine gelöscht. Niemand schreibt von Hand hinein,
-- auch Admins nicht (kein Schönfärben). Name, Art und Baustelle stehen als Kopie dabei, damit der Verlauf nach dem Umbenennen
-- oder Löschen einer Maschine lesbar bleibt. Die Zeiten zeigen die Dauer der Meldung, nicht eine Messung an der Maschine.
create table if not exists public.downtimes (
  id             bigint generated always as identity primary key,
  machine_id     uuid references public.machines(id) on delete set null,
  machine_name   text not null,
  typ            text not null default '',
  site_name      text not null default '',
  kind           text not null check (kind in ('broken', 'waiting')),
  reason         text not null default '',
  reported_name  text not null default '',
  started_at     timestamptz not null default now(),
  ended_at       timestamptz
);
create unique index if not exists downtimes_open_uq on public.downtimes(machine_id) where ended_at is null;
create index if not exists downtimes_started_idx on public.downtimes(started_at desc);

create or replace function public.downtimes_track()
returns trigger
language plpgsql security definer
set search_path = public
as $$
declare
  site_n text := '';
begin
  if tg_op = 'DELETE' then                                   -- vor dem Löschen: offene Störung abschliessen
    update public.downtimes set ended_at = now() where machine_id = old.id and ended_at is null;
    return old;
  end if;
  if tg_op = 'UPDATE' then
    if new.status is not distinct from old.status and new.reason is not distinct from old.reason then
      return new;                                            -- nichts Neues (Umbenennen, Ort wechseln, ...)
    end if;
    -- gleiche Art und gleiches Material, nur anderer Hinweis ("· ca. 20 m³"): dieselbe Störung, nicht eine neue
    if new.status in ('waiting', 'broken') and new.status = old.status
       and split_part(new.reason, ' · ', 1) = split_part(old.reason, ' · ', 1) then
      update public.downtimes set reason = new.reason where machine_id = new.id and ended_at is null;
      return new;
    end if;
  end if;
  update public.downtimes set ended_at = now() where machine_id = new.id and ended_at is null;
  if new.status in ('waiting', 'broken') then
    select coalesce(name, '') into site_n from public.sites where id = new.site_id;
    insert into public.downtimes(machine_id, machine_name, typ, site_name, kind, reason, reported_name)
    values (new.id, new.name, new.typ, coalesce(site_n, ''), new.status, new.reason, new.reported_name);
  end if;
  return new;
end;
$$;

-- AFTER, damit der Absender schon vom Trigger machines_stamp gesetzt ist. Beim Löschen BEFORE, sonst setzt die
-- Fremdschlüssel-Regel machine_id vorher auf leer und die offene Störung bliebe offen.
drop trigger if exists downtimes_trg on public.machines;
create trigger downtimes_trg
  after insert or update on public.machines
  for each row execute function public.downtimes_track();
drop trigger if exists downtimes_del_trg on public.machines;
create trigger downtimes_del_trg
  before delete on public.machines
  for each row execute function public.downtimes_track();

-- Beim ersten Ausführen: Maschinen, die jetzt schon gestört sind oder warten, bekommen einen offenen Eintrag
insert into public.downtimes(machine_id, machine_name, typ, site_name, kind, reason, reported_name, started_at)
select m.id, m.name, m.typ, coalesce(s.name, ''), m.status, m.reason, m.reported_name, coalesce(m.reported_at, now())
from public.machines m left join public.sites s on s.id = m.site_id
where m.status in ('waiting', 'broken')
  and not exists (select 1 from public.downtimes d where d.machine_id = m.id and d.ended_at is null);

alter table public.downtimes enable row level security;
drop policy if exists downtimes_select on public.downtimes;
create policy downtimes_select on public.downtimes
  for select to authenticated using (public.is_approved());
-- Keine Regel zum Schreiben, Ändern oder Löschen, und zusätzlich entzogen: nur der Trigger schreibt
revoke insert, update, delete, truncate on public.downtimes from anon, authenticated;

-- Nicht angemeldete Besucher bekommen gar keinen Zugriff
revoke all on public.profiles, public.sites, public.machines, public.needs, public.materials, public.activity, public.downtimes, public.drawings from anon;
revoke execute on function public.is_approved(), public.is_admin() from anon;

-- Rechte fuer angemeldete Benutzer ausdruecklich setzen (noetig, wenn Supabase neue Tabellen nicht automatisch freigibt).
-- Was jemand wirklich darf, bestimmen die Regeln (RLS) oben. downtimes bleibt nur lesbar.
grant usage on schema public to authenticated;
grant select, insert, update, delete on public.profiles, public.sites, public.machines, public.needs, public.materials, public.activity to authenticated;
grant select on public.downtimes to authenticated;
grant select, insert, delete on public.drawings to authenticated;     -- Zeichnungen werden nie geändert, nur gelöscht und neu gezeichnet
revoke update, truncate on public.drawings from authenticated;
grant execute on function public.is_approved(), public.is_admin() to authenticated;

-- ---------------------------------------------------------------- Echtzeit

do $$
begin
  if exists (select 1 from pg_publication where pubname = 'supabase_realtime') then
    begin
      alter publication supabase_realtime add table public.sites;
    exception when duplicate_object then null;
    end;
    begin
      alter publication supabase_realtime add table public.machines;
    exception when duplicate_object then null;
    end;
    begin
      alter publication supabase_realtime add table public.needs;
    exception when duplicate_object then null;
    end;
    begin
      alter publication supabase_realtime add table public.materials;
    exception when duplicate_object then null;
    end;
    begin
      alter publication supabase_realtime add table public.activity;
    exception when duplicate_object then null;
    end;
    begin
      alter publication supabase_realtime add table public.drawings;
    exception when duplicate_object then null;
    end;
  end if;
end $$;
