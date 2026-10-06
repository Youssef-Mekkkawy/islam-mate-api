"""
Islam Mate API — GeoNames Cities Database Builder

Downloads from GeoNames and builds a SQLite database with:
- Countries (countryInfo.txt)
- Governorates/States (admin1CodesASCII.txt)
- Districts (admin2Codes.txt)
- Cities 500+ population (cities500.zip)
- Arabic + English alternate names (alternateNamesV2.zip)

License: CC-BY 4.0 — https://creativecommons.org/licenses/by/4.0/
Attribution: GeoNames (https://www.geonames.org)

Usage:
    pip install requests
    python scripts/build_geonames_db.py
"""

from __future__ import annotations

import io
import csv
import sqlite3
import zipfile
from pathlib import Path

import requests

# ============================================
# CONFIG
# ============================================

OUT_DB = Path("data/cities.db")
CHUNK_SIZE = 8192

URLS = {
    "cities500":       "https://download.geonames.org/export/dump/cities500.zip",
    "alternateNames":  "https://download.geonames.org/export/dump/alternateNamesV2.zip",
    "admin1":          "https://download.geonames.org/export/dump/admin1CodesASCII.txt",
    "admin2":          "https://download.geonames.org/export/dump/admin2Codes.txt",
    "countryInfo":     "https://download.geonames.org/export/dump/countryInfo.txt",
    "timezones":       "https://download.geonames.org/export/dump/timeZones.txt",
}

# Only keep populated places
KEEP_FEATURE_CLASSES = {"P"}

# ============================================
# SCHEMA
# ============================================

SCHEMA = """\
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS countries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    iso2        TEXT NOT NULL UNIQUE,
    iso3        TEXT,
    name        TEXT NOT NULL,
    name_ar     TEXT,
    name_en     TEXT,
    capital     TEXT,
    continent   TEXT,
    timezone    TEXT,
    geoname_id  INTEGER
);

CREATE TABLE IF NOT EXISTS governorates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id  INTEGER NOT NULL,
    admin1_code TEXT NOT NULL,
    name        TEXT NOT NULL,
    name_ar     TEXT,
    name_en     TEXT,
    geoname_id  INTEGER,
    FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE CASCADE,
    UNIQUE(country_id, admin1_code)
);

CREATE TABLE IF NOT EXISTS districts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    governorate_id INTEGER NOT NULL,
    admin2_code TEXT NOT NULL,
    name        TEXT NOT NULL,
    name_ar     TEXT,
    name_en     TEXT,
    geoname_id  INTEGER,
    FOREIGN KEY (governorate_id) REFERENCES governorates(id) ON DELETE CASCADE,
    UNIQUE(governorate_id, admin2_code)
);

CREATE TABLE IF NOT EXISTS cities (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    geoname_id      INTEGER NOT NULL UNIQUE,
    country_id      INTEGER NOT NULL,
    governorate_id  INTEGER,
    district_id     INTEGER,
    name            TEXT NOT NULL,
    name_ar         TEXT,
    name_en         TEXT,
    latitude        REAL NOT NULL,
    longitude       REAL NOT NULL,
    timezone        TEXT NOT NULL,
    population      INTEGER DEFAULT 0,
    feature_code    TEXT,
    source_type     TEXT DEFAULT 'geonames',
    FOREIGN KEY (country_id)     REFERENCES countries(id),
    FOREIGN KEY (governorate_id) REFERENCES governorates(id),
    FOREIGN KEY (district_id)    REFERENCES districts(id)
);

CREATE INDEX IF NOT EXISTS idx_cities_name       ON cities(name);
CREATE INDEX IF NOT EXISTS idx_cities_name_ar    ON cities(name_ar);
CREATE INDEX IF NOT EXISTS idx_cities_name_en    ON cities(name_en);
CREATE INDEX IF NOT EXISTS idx_cities_geoname_id ON cities(geoname_id);
CREATE INDEX IF NOT EXISTS idx_cities_country    ON cities(country_id);
CREATE INDEX IF NOT EXISTS idx_gov_country       ON governorates(country_id);
CREATE INDEX IF NOT EXISTS idx_gov_admin1        ON governorates(admin1_code);
CREATE INDEX IF NOT EXISTS idx_dist_gov          ON districts(governorate_id);
CREATE INDEX IF NOT EXISTS idx_countries_iso2    ON countries(iso2);
"""

# ============================================
# DOWNLOAD
# ============================================

def download(url: str, label: str) -> bytes:
    print(f"Downloading {label}...")
    response = requests.get(
        url,
        stream=True,
        timeout=120,
        headers={"User-Agent": "IslamMateAPI/2.0 (https://github.com/Youssef-Mekkkawy/islam-mate-api)"}
    )
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    downloaded = 0
    chunks = []

    for chunk in response.iter_content(CHUNK_SIZE):
        chunks.append(chunk)
        downloaded += len(chunk)
        if total:
            pct = downloaded * 100 // total
            print(f"\r  {pct}% ({downloaded // 1024 // 1024} MB)", end="", flush=True)

    print()
    return b"".join(chunks)


def read_zip_text(data: bytes, filename: str) -> list[str]:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        with z.open(filename) as f:
            return f.read().decode("utf-8").splitlines()

# ============================================
# PARSE
# ============================================

def parse_timezones(lines: list[str]) -> dict[str, str]:
    """iso2 → primary timezone"""
    tz_map = {}
    for line in lines:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            country_code = parts[0].strip()
            timezone = parts[1].strip()
            if country_code not in tz_map:
                tz_map[country_code] = timezone
    return tz_map


def parse_countries(lines: list[str], tz_map: dict) -> list[dict]:
    countries = []
    for line in lines:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 17:
            continue
        iso2 = parts[0].strip()
        countries.append({
            "iso2":      iso2,
            "iso3":      parts[1].strip(),
            "name":      parts[4].strip(),
            "capital":   parts[5].strip(),
            "continent": parts[8].strip(),
            "timezone":  tz_map.get(iso2, "UTC"),
            "geoname_id": int(parts[16].strip()) if parts[16].strip().isdigit() else None,
        })
    return countries


def parse_admin1(lines: list[str]) -> dict[str, dict]:
    """Returns {country_iso2.admin1_code: {name, geoname_id}}"""
    admin1 = {}
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        code = parts[0].strip()      # e.g. EG.11
        name = parts[1].strip()
        gid  = int(parts[3].strip()) if parts[3].strip().isdigit() else None
        admin1[code] = {"name": name, "geoname_id": gid}
    return admin1


def parse_admin2(lines: list[str]) -> dict[str, dict]:
    """Returns {country.admin1.admin2: {name, geoname_id}}"""
    admin2 = {}
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        code = parts[0].strip()
        name = parts[1].strip()
        gid  = int(parts[3].strip()) if parts[3].strip().isdigit() else None
        admin2[code] = {"name": name, "geoname_id": gid}
    return admin2


def parse_cities(lines: list[str]) -> list[dict]:
    cities = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 19:
            continue
        feature_class = parts[6].strip()
        if feature_class not in KEEP_FEATURE_CLASSES:
            continue
        lat = parts[4].strip()
        lon = parts[5].strip()
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            continue

        timezone = parts[17].strip()
        if not timezone:
            continue

        cities.append({
            "geoname_id":   int(parts[0].strip()),
            "name":         parts[1].strip(),
            "latitude":     lat,
            "longitude":    lon,
            "feature_code": parts[7].strip(),
            "country_code": parts[8].strip(),
            "admin1_code":  parts[10].strip(),
            "admin2_code":  parts[11].strip(),
            "population":   int(parts[14].strip()) if parts[14].strip().isdigit() else 0,
            "timezone":     timezone,
        })
    return cities


def parse_alternate_names(lines: list[str]) -> dict[int, dict[str, str]]:
    """
    Returns {geoname_id: {"ar": "...", "en": "..."}}
    Only keeps Arabic and English alternate names.
    """
    print("Parsing alternate names (Arabic + English only)...")
    names: dict[int, dict[str, str]] = {}
    keep_langs = {"ar", "en"}

    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            continue

        lang = parts[2].strip()
        if lang not in keep_langs:
            continue

        try:
            gid = int(parts[1].strip())
        except ValueError:
            continue

        alt_name = parts[3].strip()
        is_preferred = parts[4].strip() == "1" if len(parts) > 4 else False
        is_historic = parts[8].strip() == "1" if len(parts) > 8 else False

        if is_historic:
            continue

        if gid not in names:
            names[gid] = {}

        # Prefer official/preferred name
        if lang not in names[gid] or is_preferred:
            names[gid][lang] = alt_name

    print(f"  Loaded alternate names for {len(names):,} places")
    return names

# ============================================
# BUILD DB
# ============================================

def build_db(
    countries_data: list[dict],
    admin1_data: dict,
    admin2_data: dict,
    cities_data: list[dict],
    alt_names: dict,
) -> None:

    OUT_DB.parent.mkdir(parents=True, exist_ok=True)
    if OUT_DB.exists():
        OUT_DB.unlink()
        print(f"Removed existing {OUT_DB}")

    print(f"Creating {OUT_DB}...")
    con = sqlite3.connect(OUT_DB)
    con.execute("PRAGMA foreign_keys = OFF")
    con.execute("PRAGMA journal_mode = WAL")
    con.execute("PRAGMA synchronous = NORMAL")
    con.executescript(SCHEMA)

    # --- Countries ---
    print("Inserting countries...")
    iso2_to_id = {}
    for c in countries_data:
        gid = c.get("geoname_id")
        alt = alt_names.get(gid, {}) if gid else {}
        cur = con.execute(
            """INSERT OR IGNORE INTO countries
               (iso2, iso3, name, name_ar, name_en, capital, continent, timezone, geoname_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                c["iso2"], c["iso3"], c["name"],
                alt.get("ar"), alt.get("en"),
                c["capital"], c["continent"], c["timezone"],
                gid
            )
        )
        row = con.execute("SELECT id FROM countries WHERE iso2 = ?", (c["iso2"],)).fetchone()
        if row:
            iso2_to_id[c["iso2"]] = row[0]
    con.commit()
    print(f"  {len(iso2_to_id):,} countries")

    # --- Governorates ---
    print("Inserting governorates...")
    admin1_key_to_id = {}
    for code, data in admin1_data.items():
        parts = code.split(".")
        if len(parts) != 2:
            continue
        iso2, admin1_code = parts
        country_id = iso2_to_id.get(iso2)
        if not country_id:
            continue
        gid = data.get("geoname_id")
        alt = alt_names.get(gid, {}) if gid else {}
        con.execute(
            """INSERT OR IGNORE INTO governorates
               (country_id, admin1_code, name, name_ar, name_en, geoname_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (country_id, admin1_code, data["name"], alt.get("ar"), alt.get("en"), gid)
        )
        row = con.execute(
            "SELECT id FROM governorates WHERE country_id = ? AND admin1_code = ?",
            (country_id, admin1_code)
        ).fetchone()
        if row:
            admin1_key_to_id[code] = row[0]
    con.commit()
    print(f"  {len(admin1_key_to_id):,} governorates")

    # --- Districts ---
    print("Inserting districts...")
    admin2_key_to_id = {}
    for code, data in admin2_data.items():
        parts = code.split(".")
        if len(parts) != 3:
            continue
        iso2, admin1_code, admin2_code = parts
        gov_key = f"{iso2}.{admin1_code}"
        gov_id = admin1_key_to_id.get(gov_key)
        if not gov_id:
            continue
        gid = data.get("geoname_id")
        alt = alt_names.get(gid, {}) if gid else {}
        con.execute(
            """INSERT OR IGNORE INTO districts
               (governorate_id, admin2_code, name, name_ar, name_en, geoname_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (gov_id, admin2_code, data["name"], alt.get("ar"), alt.get("en"), gid)
        )
        row = con.execute(
            "SELECT id FROM districts WHERE governorate_id = ? AND admin2_code = ?",
            (gov_id, admin2_code)
        ).fetchone()
        if row:
            admin2_key_to_id[code] = row[0]
    con.commit()
    print(f"  {len(admin2_key_to_id):,} districts")

    # --- Cities ---
    print("Inserting cities...")
    city_rows = []
    for city in cities_data:
        iso2 = city["country_code"]
        country_id = iso2_to_id.get(iso2)
        if not country_id:
            continue

        admin1_key = f"{iso2}.{city['admin1_code']}"
        gov_id = admin1_key_to_id.get(admin1_key)

        admin2_key = f"{iso2}.{city['admin1_code']}.{city['admin2_code']}"
        dist_id = admin2_key_to_id.get(admin2_key)

        gid = city["geoname_id"]
        alt = alt_names.get(gid, {})

        city_rows.append((
            gid,
            country_id,
            gov_id,
            dist_id,
            city["name"],
            alt.get("ar"),
            alt.get("en"),
            city["latitude"],
            city["longitude"],
            city["timezone"],
            city["population"],
            city["feature_code"],
        ))

    con.executemany(
        """INSERT OR IGNORE INTO cities
           (geoname_id, country_id, governorate_id, district_id,
            name, name_ar, name_en,
            latitude, longitude, timezone, population, feature_code)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        city_rows
    )
    con.commit()

    # Optimize
    print("Optimizing...")
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("VACUUM")
    con.execute("ANALYZE")
    con.close()


def verify_db() -> None:
    print("\n=== Verification ===")
    con = sqlite3.connect(OUT_DB)

    stats = {
        "Countries":    con.execute("SELECT COUNT(*) FROM countries").fetchone()[0],
        "Governorates": con.execute("SELECT COUNT(*) FROM governorates").fetchone()[0],
        "Districts":    con.execute("SELECT COUNT(*) FROM districts").fetchone()[0],
        "Cities":       con.execute("SELECT COUNT(*) FROM cities").fetchone()[0],
        "With Arabic":  con.execute("SELECT COUNT(*) FROM cities WHERE name_ar IS NOT NULL").fetchone()[0],
    }
    for k, v in stats.items():
        print(f"  {k:15}: {v:,}")

    print()

    # Test Egyptian cities
    test_cities = ["Cairo", "Sheikh Zayed", "6th of October", "Alexandria", "Giza"]
    print("=== Egypt City Tests ===")
    for city in test_cities:
        row = con.execute("""
            SELECT ci.name, ci.name_ar, ci.latitude, ci.longitude, ci.timezone, g.name
            FROM cities ci
            LEFT JOIN governorates g ON g.id = ci.governorate_id
            JOIN countries c ON c.id = ci.country_id
            WHERE c.iso2 = 'EG'
              AND (ci.name LIKE ? OR ci.name_ar LIKE ?)
            ORDER BY ci.population DESC
            LIMIT 1
        """, (f"%{city}%", f"%{city}%")).fetchone()
        if row:
            print(f"  ✅ {city}: {row[0]} ({row[1]}) → ({row[2]}, {row[3]}) {row[4]} [{row[5]}]")
        else:
            print(f"  ❌ {city}: NOT FOUND")

    con.close()


def main() -> None:
    print("=" * 55)
    print("Islam Mate API — GeoNames Database Builder")
    print("Attribution: GeoNames (CC-BY 4.0) — geonames.org")
    print("=" * 55)
    print()

    # Download all files
    country_data_raw = download(URLS["countryInfo"], "countryInfo.txt")
    timezone_raw     = download(URLS["timezones"],   "timeZones.txt")
    admin1_raw       = download(URLS["admin1"],      "admin1CodesASCII.txt")
    admin2_raw       = download(URLS["admin2"],      "admin2Codes.txt")
    cities_zip       = download(URLS["cities500"],   "cities500.zip")
    altnames_zip     = download(URLS["alternateNames"], "alternateNamesV2.zip")

    print("\nParsing data...")

    tz_map       = parse_timezones(timezone_raw.decode("utf-8").splitlines())
    countries    = parse_countries(country_data_raw.decode("utf-8").splitlines(), tz_map)
    admin1       = parse_admin1(admin1_raw.decode("utf-8").splitlines())
    admin2       = parse_admin2(admin2_raw.decode("utf-8").splitlines())
    cities       = parse_cities(read_zip_text(cities_zip, "cities500.txt"))
    alt_names    = parse_alternate_names(read_zip_text(altnames_zip, "alternateNamesV2.txt"))

    print(f"  Countries    : {len(countries):,}")
    print(f"  Governorates : {len(admin1):,}")
    print(f"  Districts    : {len(admin2):,}")
    print(f"  Cities       : {len(cities):,}")

    print("\nBuilding database...")
    build_db(countries, admin1, admin2, cities, alt_names)

    verify_db()

    db_size = OUT_DB.stat().st_size / (1024 * 1024)
    print(f"\nDatabase size: {db_size:.1f} MB")
    print(f"Location: {OUT_DB.resolve()}")
    print("\nDone! ✅")


if __name__ == "__main__":
    main()
