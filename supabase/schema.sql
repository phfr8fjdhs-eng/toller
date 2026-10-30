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

create index if not exists machines_site_idx on public.machines(site_id);
create index if not exists needs_site_idx on public.needs(site_id);
create index if not exists activity_created_idx on public.activity(created_at desc);

-- ---------------------------------------------------------------- Hilfsfunktionen

create or replace function public.is_approved()
returns boolean
language sql security definer stable
set search_path = public
as $$
  select exists (select 1 from public.profiles where id = auth.uid() and approved);
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

drop trigger if exists machines_touch on public.machines;
create trigger machines_touch
  before update on public.machines
  for each row execute function public.touch_updated_at();

-- ---------------------------------------------------------------- Zugriffsregeln (Row Level Security)

alter table public.profiles enable row level security;
alter table public.sites    enable row level security;
alter table public.machines enable row level security;
alter table public.needs    enable row level security;
alter table public.activity enable row level security;

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

-- Protokoll: lesen und ergänzen, nicht ändern
drop policy if exists activity_select on public.activity;
create policy activity_select on public.activity
  for select to authenticated using (public.is_approved());

drop policy if exists activity_insert on public.activity;
create policy activity_insert on public.activity
  for insert to authenticated with check (public.is_approved());

-- Nicht angemeldete Besucher bekommen gar keinen Zugriff
revoke all on public.profiles, public.sites, public.machines, public.needs, public.activity from anon;
revoke execute on function public.is_approved(), public.is_admin() from anon;

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
      alter publication supabase_realtime add table public.activity;
    exception when duplicate_object then null;
    end;
  end if;
end $$;
