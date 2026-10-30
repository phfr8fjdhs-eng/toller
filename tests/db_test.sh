#!/bin/bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Testet schema.sql auf einer lokalen PostgreSQL mit nachgebautem Supabase-Rahmen
set -e
BIN=/usr/lib/postgresql/16/bin
D=/tmp/pgtest
rm -rf $D && mkdir -p $D && chown postgres $D
su postgres -c "$BIN/initdb -D $D/data -A trust >/dev/null"
su postgres -c "$BIN/pg_ctl -D $D/data -o '-p 5544 -k $D' -l $D/log -w start >/dev/null"
P="psql -h $D -p 5544 -U postgres -v ON_ERROR_STOP=1 -q -X"
$P -d postgres -c "create database t"
P="$P -d t"

$P <<'SQL'
create role anon nologin; create role authenticated nologin;
create schema auth;
create table auth.users (id uuid primary key default gen_random_uuid(), email text, raw_user_meta_data jsonb default '{}');
create function auth.uid() returns uuid language sql stable as $$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
grant usage on schema auth to anon, authenticated;
grant usage on schema public to anon, authenticated;
alter default privileges in schema public grant all on tables to anon, authenticated;
alter default privileges in schema public grant all on sequences to anon, authenticated;
alter default privileges in schema public grant execute on functions to anon, authenticated;
SQL

echo "--- Schema zweimal ausfuehren (muss wiederholbar sein)"
$P -f "$(cd "$(dirname "$0")/.." && pwd)"/supabase/schema.sql
$P -f "$(cd "$(dirname "$0")/.." && pwd)"/supabase/schema.sql
echo "OK"
echo "--- Beispieldaten"
$P -f "$(cd "$(dirname "$0")/.." && pwd)"/supabase/beispieldaten.sql
$P -At -c "select (select count(*) from sites)||' Baustellen, '||(select count(*) from machines)||' Maschinen'"
P="psql -h $D -p 5544 -U postgres -d t -At -X -q"

U1=11111111-1111-1111-1111-111111111111   # erste Person -> Admin
U2=22222222-2222-2222-2222-222222222222   # zweite Person -> nicht freigegeben
U3=33333333-3333-3333-3333-333333333333   # Mitarbeiter, spaeter freigegeben

$P -c "insert into auth.users(id,email,raw_user_meta_data) values ('$U1','chef@firma.test','{\"name\":\"Chef\"}'),('$U2','neu@firma.test','{}')"
$P -c "insert into auth.users(id,email) values ('$U3','ma@firma.test')"

echo "1) Profile nach Registrierung (Erwartung: Chef=admin/true, neu=mitarbeiter/false, ma=mitarbeiter/false)"
$P -c "select name||'='||role||'/'||approved from public.profiles order by created_at, email"

# Hilfsfunktion: als eingeloggter Benutzer ausfuehren (Fehler werden angezeigt, nicht abgebrochen)
as_user () { # $1=uuid  $2=sql
  psql -h $D -p 5544 -U postgres -d t -At -X -q 2>&1 <<SQL
set role authenticated; select set_config('request.jwt.claim.sub','$1',false);
$2
SQL
}
as_anon () { psql -h $D -p 5544 -U postgres -d t -At -X -q 2>&1 <<SQL
set role anon;
$1
SQL
}

echo "2) Nicht angemeldet liest Baustellen (Erwartung: permission denied)"
as_anon "select count(*) from public.sites;" | head -2

echo "3) Nicht freigegebene Person liest Baustellen (Erwartung: 0 Zeilen)"
as_user $U2 "select count(*) from public.sites;"
echo "4) Nicht freigegebene Person legt Baustelle an (Erwartung: Fehler row-level security)"
as_user $U2 "insert into public.sites(name,sparte,lat,lng) values ('Hack','tief',47,8);" | head -2
echo "5) Nicht freigegebene Person gibt sich selbst frei (Erwartung: 0 Zeilen geaendert)"
as_user $U2 "update public.profiles set approved=true, role='admin' where id='$U2' returning id;"
$P -c "select 'danach approved='||approved||' role='||role from public.profiles where id='$U2'"
echo "6) Nicht freigegebene Person sieht fremde Profile (Erwartung: nur 1 = das eigene)"
as_user $U2 "select count(*) from public.profiles;"

echo "7) Admin sieht alles (Erwartung: 5 Baustellen, 3 Profile)"
as_user $U1 "select (select count(*) from public.sites)||' Baustellen, '||(select count(*) from public.profiles)||' Profile';"
echo "8) Admin gibt U3 frei"
as_user $U1 "update public.profiles set approved=true where id='$U3' returning name;"

echo "9) Freigegebener Mitarbeiter sieht 5 Baustellen und legt eine an (Erwartung: 5, dann INSERT-Zeile)"
as_user $U3 "select count(*) from public.sites;"
as_user $U3 "insert into public.sites(name,sparte,material_name,lat,lng) values ('Neue Baustelle','garten','Kies',47.2,8.8) returning created_by='$U3';"
echo "10) Mitarbeiter aendert Maschinenstatus (Erwartung: 1 Zeile, Status broken)"
as_user $U3 "update public.machines set status='broken', reason='' where name='Bagger 1' returning status;"
echo "11) Mitarbeiter loescht Baustelle (Erwartung: 0 Zeilen, nicht erlaubt)"
as_user $U3 "delete from public.sites where name='Neue Baustelle' returning id;"
$P -c "select 'Baustelle noch da: '||count(*) from public.sites where name='Neue Baustelle'"
echo "12) Mitarbeiter macht sich zum Admin (Erwartung: 0 Zeilen)"
as_user $U3 "update public.profiles set role='admin' where id='$U3' returning id;"
echo "13) Mitarbeiter schreibt Protokoll (Erwartung: eine Zeile), ungueltige Werte (Erwartung: Fehler)"
as_user $U3 "insert into public.activity(text) values ('Bagger 1 ausgefallen') returning id;"
as_user $U3 "insert into public.machines(name,sparte,status) values ('X','tief','kaputt');" | head -1
as_user $U3 "insert into public.sites(name,sparte,lat,lng) values ('Y','tief',999,8);" | head -1

echo "14) Admin loescht Baustelle (Erwartung: eine id)"
as_user $U1 "delete from public.sites where name='Neue Baustelle' returning name;"
echo "15) Admin loescht sich selbst (Erwartung: 0 Zeilen)"
as_user $U1 "delete from public.profiles where id='$U1' returning id;"
echo "16) Maschine nach Loeschen der Baustelle: site_id wird leer (Erwartung: 0 Maschinen mit kaputter Verknuepfung)"
$P -c "delete from public.sites where name='Birkenweg'"
$P -c "select count(*) from public.machines where site_id is not null and site_id not in (select id from public.sites)"
echo "17) updated_at wird gesetzt (Erwartung: t)"
$P -c "select updated_at > now() - interval '1 minute' from public.machines where name='Bagger 1'"
