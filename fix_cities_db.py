# Fix UNIQUE constraint error — change INSERT to INSERT OR IGNORE

content = open('scripts/build_cities_db.py', 'r', encoding='utf-8').read()

content = content.replace(
    '"INSERT INTO governorates (id, country_id, name, name_local, code) VALUES (?, ?, ?, ?, ?)"',
    '"INSERT OR IGNORE INTO governorates (id, country_id, name, name_local, code) VALUES (?, ?, ?, ?, ?)"'
)

content = content.replace(
    '"INSERT INTO countries (id, name, name_local, iso2, iso3, timezone) VALUES (?, ?, ?, ?, ?, ?)"',
    '"INSERT OR IGNORE INTO countries (id, name, name_local, iso2, iso3, timezone) VALUES (?, ?, ?, ?, ?, ?)"'
)

content = content.replace(
    '"""INSERT INTO cities',
    '"""INSERT OR IGNORE INTO cities'
)

open('scripts/build_cities_db.py', 'w', encoding='utf-8').write(content)
print('Fixed!')
