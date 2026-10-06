"""
Build the Islam Mate prayer location dataset.

Source:
    dr5hn/countries-states-cities-database
    https://github.com/dr5hn/countries-states-cities-database
    License: ODbL-1.0

Output:
    data/cities.db (SQLite)

Hierarchy:
    Country -> Governorate/State/Region -> City

No districts or neighborhoods.

Usage:
    python scripts/build_cities_db.py

Requirements:
    pip install requests
"""

from __future__ import annotations

import gzip
import json
import sqlite3
from pathlib import Path
from typing import Any

import requests


SOURCE_URL = (
    "https://github.com/dr5hn/"
    "countries-states-cities-database/releases/latest/download/"
    "json-countries%2Bstates%2Bcities.json.gz"
)

# Output to data/ folder — consistent with other Islam Mate data files
OUT_DB = Path("data/cities.db")

# Attribution required by ODbL-1.0
ATTRIBUTION = "Data: © OpenStreetMap contributors / dr5hn (ODbL-1.0)"

# City-level settlement types
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
}

SCHEMA = """\
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS countries (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    name_local TEXT,
    iso2 TEXT NOT NULL UNIQUE,
    iso3 TEXT,
    timezone TEXT
);

CREATE TABLE IF NOT EXISTS governorates (
    id INTEGER PRIMARY KEY,
    country_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    name_local TEXT,
    code TEXT,
    FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE CASCADE,
    UNIQUE(country_id, name)
);

CREATE TABLE IF NOT EXISTS cities (
    id INTEGER PRIMARY KEY,
    governorate_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    name_local TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    timezone TEXT NOT NULL,
    source_id INTEGER,
    source_type TEXT,
    FOREIGN KEY (governorate_id) REFERENCES governorates(id) ON DELETE CASCADE,
    UNIQUE(governorate_id, name, latitude, longitude)
);

CREATE INDEX IF NOT EXISTS idx_governorates_country
    ON governorates(country_id);

CREATE INDEX IF NOT EXISTS idx_cities_governorate
    ON cities(governorate_id);

CREATE INDEX IF NOT EXISTS idx_cities_name
    ON cities(name);

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
"""


def download_source() -> list[dict[str, Any]]:
    print("Downloading geographic dataset from dr5hn...")
    response = requests.get(
        SOURCE_URL,
        timeout=120,
        headers={"User-Agent": "IslamMateAPI/1.0"},
    )
    response.raise_for_status()

    print("Decompressing...")
    raw = gzip.decompress(response.content)
    data = json.loads(raw.decode("utf-8"))

    if not isinstance(data, list):
        raise RuntimeError("Unexpected source format.")

    print(f"Downloaded {len(data)} countries.")
    return data


def text_or_none(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None


def build(
    source: list[dict[str, Any]]
) -> tuple[list[tuple], list[tuple], list[tuple]]:

    country_rows = []
    governorate_rows = []
    city_rows = []

    next_country_id = 1
    next_governorate_id = 1
    next_city_id = 1
    next_district_id = 1
    district_rows = []

    for country in source:
        country_id = int(country.get("id") or next_country_id)
        next_country_id = max(next_country_id, country_id + 1)

        country_name = str(country.get("name") or "").strip()
        if not country_name:
            continue

        iso2 = str(
            country.get("iso2") or
            country.get("iso2Code") or
            country.get("code") or ""
        ).upper()

        iso3 = text_or_none(country.get("iso3"))

        # Get primary timezone
        country_timezone = None
        tzs = country.get("timezones")
        if isinstance(tzs, list) and tzs:
            first = tzs[0]
            if isinstance(first, dict):
                country_timezone = first.get("zoneName")
            elif isinstance(first, str):
                country_timezone = first

        country_rows.append((
            country_id,
            country_name,
            text_or_none(country.get("native")),
            iso2,
            iso3,
            country_timezone,
        ))

        for state in country.get("states") or []:
            governorate_id = int(state.get("id") or next_governorate_id)
            next_governorate_id = max(next_governorate_id, governorate_id + 1)

            state_name = str(state.get("name") or "").strip()
            if not state_name:
                continue

            state_code = text_or_none(
                state.get("state_code") or state.get("code")
            )

            governorate_rows.append((
                governorate_id,
                country_id,
                state_name,
                text_or_none(state.get("native")),
                state_code,
            ))

            for city in state.get("cities") or []:
                city_type = city.get("type")

                # Skip districts and neighborhoods
                if city_type == "section":
                    continue
                if city_type not in KEEP_CITY_TYPES:
                    continue

                city_name = str(city.get("name") or "").strip()
                if not city_name:
                    continue

                lat = city.get("latitude")
                lon = city.get("longitude")
                timezone = city.get("timezone")

                # Skip entries without coordinates or timezone
                if lat in (None, "") or lon in (None, "") or timezone in (None, ""):
                    continue

                try:
                    lat = float(lat)
                    lon = float(lon)
                except (TypeError, ValueError):
                    continue

                city_id = int(city.get("id") or next_city_id)
                next_city_id = max(next_city_id, city_id + 1)

                city_rows.append((
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

    return country_rows, governorate_rows, city_rows, district_rows


def write_db(
    countries: list[tuple],
    governorates: list[tuple],
    cities: list[tuple],
    districts: list[tuple],
) -> None:
    OUT_DB.parent.mkdir(parents=True, exist_ok=True)

    if OUT_DB.exists():
        OUT_DB.unlink()
        print(f"Removed existing {OUT_DB}")

    print(f"Creating {OUT_DB}...")
    con = sqlite3.connect(OUT_DB)

    try:
        con.executescript(SCHEMA)
        con.execute("PRAGMA foreign_keys = OFF")

        print("Inserting countries...")
        con.executemany(
            "INSERT OR IGNORE INTO countries (id, name, name_local, iso2, iso3, timezone) VALUES (?, ?, ?, ?, ?, ?)",
            countries,
        )

        print("Inserting governorates...")
        con.executemany(
            "INSERT OR IGNORE INTO governorates (id, country_id, name, name_local, code) VALUES (?, ?, ?, ?, ?)",
            governorates,
        )

        print("Inserting cities...")
        con.executemany(
            """INSERT OR IGNORE INTO cities
               (id, governorate_id, name, name_local, latitude, longitude, timezone, source_id, source_type)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            cities,
        )

        print("Inserting districts...")
        con.executemany(
            """INSERT OR IGNORE INTO districts
               (id, city_id, name, name_local, latitude, longitude, timezone, source_id, source_type)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            districts,
        )

        con.commit()
        con.execute("PRAGMA foreign_keys = ON")

        # Optimize the DB
        print("Optimizing...")
        con.execute("VACUUM")
        con.execute("ANALYZE")

    finally:
        con.close()


def verify_db() -> None:
    """Quick sanity check after build."""
    con = sqlite3.connect(OUT_DB)
    try:
        # Test Egypt/Giza/6th of October query
        row = con.execute("""
            SELECT c.name, g.name, ci.name, ci.latitude, ci.longitude, ci.timezone
            FROM cities ci
            JOIN governorates g ON g.id = ci.governorate_id
            JOIN countries c ON c.id = g.country_id
            WHERE c.iso2 = 'EG' AND ci.name LIKE '%October%'
            LIMIT 1
        """).fetchone()

        if row:
            print(f"\nVerification: {row[0]} / {row[1]} / {row[2]} → ({row[3]}, {row[4]}) {row[5]}")
        else:
            print("\nVerification: Egypt/October city not found (may have different name in dataset)")

        # Test Arabic search
        ar_row = con.execute("""
            SELECT ci.name, ci.name_local, ci.latitude, ci.longitude
            FROM cities ci
            WHERE ci.name_local LIKE '%القاهرة%'
            LIMIT 1
        """).fetchone()

        if ar_row:
            print(f"Arabic search: {ar_row[0]} ({ar_row[1]}) → ({ar_row[2]}, {ar_row[3]})")
        else:
            print("Arabic search: No Arabic name found for Cairo (may be missing in dataset)")

    finally:
        con.close()


def main() -> None:
    print("=" * 50)
    print("Islam Mate API — Cities Database Builder")
    print(ATTRIBUTION)
    print("=" * 50)
    print()

    source = download_source()

    print("Building hierarchy...")
    countries, governorates, cities, districts = build(source)

    write_db(countries, governorates, cities, districts)

    verify_db()

    db_size = OUT_DB.stat().st_size / (1024 * 1024)

    print()
    print("=" * 50)
    print("Done!")
    print(f"Countries    : {len(countries):,}")
    print(f"Governorates : {len(governorates):,}")
    print(f"Cities       : {len(cities):,}")
    print(f"Districts    : {len(districts):,}")
    print(f"Database     : {OUT_DB.resolve()}")
    print(f"Size         : {db_size:.1f} MB")
    print("=" * 50)


if __name__ == "__main__":
    main()
