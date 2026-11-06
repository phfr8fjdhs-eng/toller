-- OPTIONAL: Beispieldaten, damit das Dashboard nicht leer ist.
-- Nur ausführen, wenn du sie zum Ausprobieren willst. Alle Namen sind erfunden.
-- Später kannst du sie im Dashboard als Admin löschen.

insert into public.sites (name, sparte, weitere_sparten, lat, lng) values
  ('Birkenweg', 'garten', '{}', 47.2300, 8.8420),
  ('Umfahrung Nord', 'strasse', '{}', 47.2560, 8.8480),
  ('Kanal Bahnhofstr.', 'tief', '{strasse}', 47.2258, 8.8212),   -- Tiefbau und Strassenbau zusammen
  ('Park Seeblick', 'garten', '{}', 47.2335, 8.8185),
  ('Kreisel Eschenbach', 'strasse', '{}', 47.2406, 8.9221);

insert into public.machines (name, typ, sparte, site_id, status) values
  ('Bagger 1',      'Bagger',     'tief',    (select id from public.sites where name = 'Kanal Bahnhofstr.'), 'running'),
  ('Minibagger 1',  'Minibagger', 'tief',    (select id from public.sites where name = 'Kanal Bahnhofstr.'), 'running'),
  ('Dumper 1',      'Dumper',     'tief',    (select id from public.sites where name = 'Kanal Bahnhofstr.'), 'running'),
  ('Walze 1',       'Walze',      'strasse', (select id from public.sites where name = 'Umfahrung Nord'), 'running'),
  ('Fertiger 1',    'Fertiger',   'strasse', (select id from public.sites where name = 'Umfahrung Nord'), 'running'),
  ('LKW 1',         'LKW',        'strasse', (select id from public.sites where name = 'Umfahrung Nord'), 'running'),
  ('Radlader 1',    'Radlader',   'strasse', (select id from public.sites where name = 'Kreisel Eschenbach'), 'running'),
  ('Minibagger 2',  'Minibagger', 'garten',  (select id from public.sites where name = 'Birkenweg'), 'running'),
  ('Dumper 2',      'Dumper',     'garten',  (select id from public.sites where name = 'Birkenweg'), 'running'),
  ('Radlader 2',    'Radlader',   'garten',  (select id from public.sites where name = 'Park Seeblick'), 'running'),
  ('Bagger 2',      'Bagger',     'tief',    null, 'off'),
  ('LKW 2',         'LKW',        'strasse', null, 'off'),
  ('Teleskoplader', 'Teleskoplader', 'garten', null, 'off');
