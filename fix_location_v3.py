content = open('modules/location/module.py', 'r', encoding='utf-8').read()

# Fix 1: Better DB search — exact match first, then partial
old_db_search = '''    def _db_search(self, q: str, limit: int = 5) -> list[dict]:
        """Search cities.db for a city name (English or Arabic)."""
        if not DB_PATH.exists():
            return []

        try:
            con = sqlite3.connect(DB_PATH)
            con.row_factory = sqlite3.Row
            rows = con.execute("""
                SELECT
                    ci.name,
                    ci.name_local,
                    ci.latitude,
                    ci.longitude,
                    ci.timezone,
                    g.name AS governorate,
                    c.name AS country,
                    c.iso2
                FROM cities ci
                JOIN governorates g ON g.id = ci.governorate_id
                JOIN countries c ON c.id = g.country_id
                WHERE ci.name LIKE ?
                   OR ci.name_local LIKE ?
                   OR g.name LIKE ?
                LIMIT ?
            """, (f"%{q}%", f"%{q}%", f"%{q}%", limit)).fetchall()
            con.close()

            return [dict(r) for r in rows]
        except Exception:
            return []'''

new_db_search = '''    def _db_search(self, q: str, limit: int = 5) -> list[dict]:
        """Search cities.db — exact match first, then partial."""
        if not DB_PATH.exists():
            return []

        try:
            con = sqlite3.connect(DB_PATH)
            con.row_factory = sqlite3.Row

            # Try exact match first
            rows = con.execute("""
                SELECT
                    ci.name,
                    ci.name_local,
                    ci.latitude,
                    ci.longitude,
                    ci.timezone,
                    g.name AS governorate,
                    c.name AS country,
                    c.iso2
                FROM cities ci
                JOIN governorates g ON g.id = ci.governorate_id
                JOIN countries c ON c.id = g.country_id
                WHERE ci.name = ? OR ci.name_local = ?
                ORDER BY
                    CASE WHEN ci.name = ? THEN 0 ELSE 1 END
                LIMIT ?
            """, (q, q, q, limit)).fetchall()

            # If no exact match, try partial
            if not rows:
                rows = con.execute("""
                    SELECT
                        ci.name,
                        ci.name_local,
                        ci.latitude,
                        ci.longitude,
                        ci.timezone,
                        g.name AS governorate,
                        c.name AS country,
                        c.iso2
                    FROM cities ci
                    JOIN governorates g ON g.id = ci.governorate_id
                    JOIN countries c ON c.id = g.country_id
                    WHERE ci.name LIKE ? OR ci.name_local LIKE ?
                    ORDER BY
                        CASE WHEN ci.name LIKE ? THEN 0 ELSE 1 END
                    LIMIT ?
                """, (f"{q}%", f"{q}%", f"{q}%", limit)).fetchall()

            # If still nothing, full partial match
            if not rows:
                rows = con.execute("""
                    SELECT
                        ci.name,
                        ci.name_local,
                        ci.latitude,
                        ci.longitude,
                        ci.timezone,
                        g.name AS governorate,
                        c.name AS country,
                        c.iso2
                    FROM cities ci
                    JOIN governorates g ON g.id = ci.governorate_id
                    JOIN countries c ON c.id = g.country_id
                    WHERE ci.name LIKE ? OR ci.name_local LIKE ?
                    LIMIT ?
                """, (f"%{q}%", f"%{q}%", limit)).fetchall()

            con.close()
            return [dict(r) for r in rows]
        except Exception:
            return []'''

content = content.replace(old_db_search, new_db_search)

# Fix 2: Cache uses city name for lookup (not just name LIKE)
old_cache_check = '''        try:
            con = sqlite3.connect(DB_PATH)

            # Get or create country'''

new_cache_check = '''        try:
            con = sqlite3.connect(DB_PATH)

            # Check if already cached
            existing = con.execute(
                "SELECT id FROM cities WHERE name = ? AND source_type = 'nominatim_cache'",
                (result["name"],)
            ).fetchone()
            if existing:
                con.close()
                return

            # Get or create country'''

content = content.replace(old_cache_check, new_cache_check)

open('modules/location/module.py', 'w', encoding='utf-8').write(content)
print('Done!')
