content = open('scripts/build_cities_db.py', 'r', encoding='utf-8').read()

# 1. Update schema to add districts table
old_schema_end = """\
CREATE INDEX IF NOT EXISTS idx_cities_name_local
    ON cities(name_local);

CREATE INDEX IF NOT EXISTS idx_countries_iso2
    ON countries(iso2);
\"\"\""""

new_schema_end = """\
CREATE INDEX IF NOT EXISTS idx_cities_name_local
    ON cities(name_local);

CREATE INDEX IF NOT EXISTS idx_countries_iso2
    ON countries(iso2);

CREATE TABLE IF NOT EXISTS districts (
    id INTEGER PRIMARY KEY,
    city_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    name_local TEXT,
    latitude REAL,
    longitude REAL,
    timezone TEXT,
    source_id INTEGER,
    source_type TEXT,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    UNIQUE(city_id, name)
);

CREATE INDEX IF NOT EXISTS idx_districts_city
    ON districts(city_id);

CREATE INDEX IF NOT EXISTS idx_districts_name
    ON districts(name);

CREATE INDEX IF NOT EXISTS idx_districts_name_local
    ON districts(name_local);
\"\"\""""

content = content.replace(old_schema_end, new_schema_end)

# 2. Add district_rows list in build()
old_build_return = "    return country_rows, governorate_rows, city_rows"
new_build_return = "    return country_rows, governorate_rows, city_rows, district_rows"

content = content.replace(old_build_return, new_build_return)

# 3. Initialize district_rows in build()
old_init = "    next_city_id = 1\n\n    for country in source:"
new_init = "    next_city_id = 1\n    next_district_id = 1\n    district_rows = []\n\n    for country in source:"

content = content.replace(old_init, new_init)

# 4. Add district types to KEEP_CITY_TYPES and create DISTRICT_TYPES
old_keep = """# Only keep settlement-level city types — no districts or neighborhoods
KEEP_CITY_TYPES = {
    "city",
    "town",
    "village",
    "locality",
    "capital",
    "municipality",
    "settlement",
    "township",
    "cities",
    None,
}"""

new_keep = """# City-level settlement types
KEEP_CITY_TYPES = {
    "city",
    "town",
    "village",
    "locality",
    "capital",
    "municipality",
    "settlement",
    "township",
    "cities",
    None,
}

# District-level types — stored separately
DISTRICT_TYPES = {
    "district",
    "subdistrict",
    "section",
    "suburb",
    "neighborhood",
    "quarter",
    "adm3",
    "adm4",
    "adm5",
}"""

content = content.replace(old_keep, new_keep)

# 5. After city_rows.append(), add district handling
old_city_append = """                city_rows.append((
                    city_id,
                    governorate_id,
                    city_name,
                    text_or_none(city.get("native")),
                    lat,
                    lon,
                    str(timezone),
                    city_id,
                    text_or_none(city_type),
                ))

            country_out["governorates"].append(governorate_out)"""

new_city_append = """                city_rows.append((
                    city_id,
                    governorate_id,
                    city_name,
                    text_or_none(city.get("native")),
                    lat,
                    lon,
                    str(timezone),
                    city_id,
                    text_or_none(city_type),
                ))

                # Add sub-localities as districts
                for sub in city.get("districts") or []:
                    sub_name = str(sub.get("name") or "").strip()
                    if not sub_name:
                        continue
                    sub_lat = sub.get("latitude")
                    sub_lon = sub.get("longitude")
                    sub_tz = sub.get("timezone") or str(timezone)
                    try:
                        sub_lat = float(sub_lat) if sub_lat else lat
                        sub_lon = float(sub_lon) if sub_lon else lon
                    except (TypeError, ValueError):
                        sub_lat, sub_lon = lat, lon
                    district_id = int(sub.get("id") or next_district_id)
                    next_district_id = max(next_district_id, district_id + 1)
                    district_rows.append((
                        district_id,
                        city_id,
                        sub_name,
                        text_or_none(sub.get("native")),
                        sub_lat,
                        sub_lon,
                        sub_tz,
                        district_id,
                        None,
                    ))

            country_out["governorates"].append(governorate_out)"""

content = content.replace(old_city_append, new_city_append)

# 6. Update write_db signature
old_sig = "def write_db(\n    countries: list[tuple],\n    governorates: list[tuple],\n    cities: list[tuple],\n) -> None:"
new_sig = "def write_db(\n    countries: list[tuple],\n    governorates: list[tuple],\n    cities: list[tuple],\n    districts: list[tuple],\n) -> None:"

content = content.replace(old_sig, new_sig)

# 7. Add district insert in write_db
old_vacuum = '        con.commit()\n        con.execute("PRAGMA foreign_keys = ON")'
new_vacuum = '''        print("Inserting districts...")
        con.executemany(
            """INSERT OR IGNORE INTO districts
               (id, city_id, name, name_local, latitude, longitude, timezone, source_id, source_type)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            districts,
        )

        con.commit()
        con.execute("PRAGMA foreign_keys = ON")'''

content = content.replace(old_vacuum, new_vacuum)

# 8. Update write_db call in main()
old_call = "    write_db(countries, governorates, cities)"
new_call = "    write_db(countries, governorates, cities, districts)"

content = content.replace(old_call, new_call)

# 9. Update build() call
old_build_call = "    countries, governorates, cities = build(source)"
new_build_call = "    countries, governorates, cities, districts = build(source)"

content = content.replace(old_build_call, new_build_call)

# 10. Update stats print
old_stats = '''    print(f"Cities       : {len(cities):,}")'''
new_stats = '''    print(f"Cities       : {len(cities):,}")
    print(f"Districts    : {len(districts):,}")'''

content = content.replace(old_stats, new_stats)

open('scripts/build_cities_db.py', 'w', encoding='utf-8').write(content)
print('Done! Script updated with districts support.')
