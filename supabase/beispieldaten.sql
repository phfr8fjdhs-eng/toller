-- OPTIONAL: Beispieldaten, damit das Dashboard nicht leer ist.
-- Nur ausführen, wenn du sie zum Ausprobieren willst. Alle Namen sind erfunden.
-- Später kannst du sie im Dashboard als Admin löschen.

insert into public.sites (name, sparte, material_name, material_level, lat, lng) values
  ('Birkenweg',          'garten',  'Humus',    80, 47.2300, 8.8420),
  ('Umfahrung Nord',     'strasse', 'Asphalt',  70, 47.2560, 8.8480),
  ('Kanal Bahnhofstr.',  'tief',    'Kies',     60, 47.2258, 8.8212),
  ('Park Seeblick',      'garten',  'Pflanzen', 45, 47.2335, 8.8185),
  ('Kreisel Eschenbach', 'strasse', 'Beton',    90, 47.2406, 8.9221);

insert into public.machines (name, typ, sparte, site_id, status, tank) values
  ('Bagger 1',      'Bagger',     'tief',    (select id from public.sites where name = 'Kanal Bahnhofstr.'),  'running', 80),
  ('Minibagger 1',  'Minibagger', 'tief',    (select id from public.sites where name = 'Kanal Bahnhofstr.'),  'running', 60),
  ('Dumper 1',      'Dumper',     'tief',    (select id from public.sites where name = 'Kanal Bahnhofstr.'),  'running', 90),
  ('Walze 1',       'Walze',      'strasse', (select id from public.sites where name = 'Umfahrung Nord'),     'running', 70),
  ('Fertiger 1',    'Fertiger',   'strasse', (select id from public.sites where name = 'Umfahrung Nord'),     'running', 85),
  ('LKW 1',         'LKW',        'strasse', (select id from public.sites where name = 'Umfahrung Nord'),     'running', 50),
  ('Radlader 1',    'Radlader',   'strasse', (select id from public.sites where name = 'Kreisel Eschenbach'), 'running', 75),
  ('Minibagger 2',  'Minibagger', 'garten',  (select id from public.sites where name = 'Birkenweg'),          'running', 80),
  ('Dumper 2',      'Dumper',     'garten',  (select id from public.sites where name = 'Birkenweg'),          'running', 55),
  ('Radlader 2',    'Radlader',   'garten',  (select id from public.sites where name = 'Park Seeblick'),      'running', 90),
  ('Bagger 2',      'Bagger',     'tief',    null, 'off', 100),
  ('LKW 2',         'LKW',        'strasse', null, 'off', 100),
  ('Teleskoplader', 'Teleskoplader', 'garten', null, 'off', 100);
