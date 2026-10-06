from fastapi import APIRouter, Query, Request
from base.base_module import BaseModule
import httpx
import sqlite3
from pathlib import Path


DB_PATH = Path("data/cities.db")


class Module(BaseModule):
    name = "location"
    version = "2.0.0"
    dependencies = []

    def register_routes(self, router: APIRouter):
        router.add_api_route(
            "/location/detect",
            self.detect,
            methods=["GET"],
            summary="Detect location from IP",
            tags=["Location"]
        )
        router.add_api_route(
            "/location/search",
            self.search,
            methods=["GET"],
            summary="Search city by name",
            tags=["Location"]
        )
        router.add_api_route(
            "/prayer-times/auto",
            self.prayer_times_auto,
            methods=["GET"],
            summary="Auto prayer times from IP",
            tags=["Location"]
        )

    # ============================================
    # DB HELPERS
    # ============================================

    def _db_search(self, q: str, limit: int = 5) -> list[dict]:
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
            return []

    def _cache_to_db(self, result: dict) -> None:
        """Cache a Nominatim result into cities.db for offline use later."""
        if not DB_PATH.exists():
            return

        try:
            con = sqlite3.connect(DB_PATH)

            # Check if already cached
            existing = con.execute(
                "SELECT id FROM cities WHERE name = ? AND source_type = 'nominatim_cache'",
                (result["name"],)
            ).fetchone()
            if existing:
                con.close()
                return

            # Get or create country
            country_row = con.execute(
                "SELECT id FROM countries WHERE name = ?",
                (result["country"],)
            ).fetchone()

            if country_row:
                country_id = country_row[0]
            else:
                cur = con.execute(
                    "INSERT OR IGNORE INTO countries (name, iso2, timezone) VALUES (?, ?, ?)",
                    (result["country"], result.get("country_code", "XX").upper(), result.get("timezone", "UTC"))
                )
                country_id = cur.lastrowid

            # Get or create governorate
            gov_name = result.get("governorate") or result["country"]
            gov_row = con.execute(
                "SELECT id FROM governorates WHERE country_id = ? AND name = ?",
                (country_id, gov_name)
            ).fetchone()

            if gov_row:
                governorate_id = gov_row[0]
            else:
                cur = con.execute(
                    "INSERT OR IGNORE INTO governorates (country_id, name) VALUES (?, ?)",
                    (country_id, gov_name)
                )
                governorate_id = cur.lastrowid

            # Insert city
            con.execute("""
                INSERT OR IGNORE INTO cities
                (governorate_id, name, name_local, latitude, longitude, timezone, source_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                governorate_id,
                result["name"],
                result.get("name_local"),
                result["latitude"],
                result["longitude"],
                result.get("timezone", "UTC"),
                "nominatim_cache"
            ))

            con.commit()
            con.close()
        except Exception:
            pass  # Cache failure is not critical

    # ============================================
    # NOMINATIM FALLBACK
    # ============================================

    async def _nominatim_search(self, q: str, lang: str = "en", limit: int = 5) -> list[dict]:
        """Search Nominatim (OpenStreetMap) for a city."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "q": q,
                        "format": "json",
                        "limit": limit,
                        "addressdetails": 1,
                        "accept-language": lang,
                    },
                    headers={"User-Agent": "IslamMateAPI/2.0"},
                    timeout=10.0
                )
                results = response.json()

            cities = []
            for r in results:
                address = r.get("address", {})
                city_name = (
                    address.get("city") or
                    address.get("town") or
                    address.get("village") or
                    address.get("county") or
                    r.get("display_name", "").split(",")[0]
                )
                country = address.get("country", "")
                country_code = address.get("country_code", "").upper()
                state = address.get("state", "")

                city = {
                    "name": city_name,
                    "name_local": None,
                    "country": country,
                    "country_code": country_code,
                    "governorate": state,
                    "latitude": float(r.get("lat", 0)),
                    "longitude": float(r.get("lon", 0)),
                    "timezone": None,
                    "display_name": r.get("display_name", ""),
                    "source": "nominatim"
                }
                cities.append(city)

                # Cache to DB for offline use
                self._cache_to_db(city)

            return cities
        except Exception:
            return []

    # ============================================
    # ENDPOINTS
    # ============================================

    async def detect(
        self,
        request: Request,
        lang: str = Query("en", description="Language: en or ar")
    ):
        lang = self.get_lang(request, lang)

        ip = request.headers.get("X-Forwarded-For")
        if ip:
            ip = ip.split(",")[0].strip()
        else:
            ip = request.client.host

        if ip in ("127.0.0.1", "::1", "localhost"):
            return {
                "ip": ip,
                "city": self.translate({"ar": "غير متاح محلياً", "en": "Not available locally"}, lang),
                "country": self.translate({"ar": "اختبار محلي", "en": "Local testing"}, lang),
                "latitude": None,
                "longitude": None,
                "timezone": None,
                "note": self.translate({
                    "ar": "لا يمكن كشف الموقع من localhost. أرسل latitude و longitude يدوياً.",
                    "en": "Cannot detect location from localhost. Pass latitude and longitude manually."
                }, lang)
            }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://ip-api.com/json/{ip}",
                params={"fields": "status,message,country,city,lat,lon,timezone,query"},
                timeout=5.0
            )
            data = response.json()

        if data.get("status") != "success":
            return {
                "error": self.translate({
                    "ar": "فشل في كشف الموقع",
                    "en": "Failed to detect location"
                }, lang),
                "message": data.get("message", "Unknown error")
            }

        return {
            "ip": data.get("query"),
            "city": data.get("city"),
            "country": data.get("country"),
            "latitude": data.get("lat"),
            "longitude": data.get("lon"),
            "timezone": data.get("timezone"),
            "source": "ip-api",
            "accuracy": self.translate({
                "ar": "دقة المدينة (+/- 10-50 كم)",
                "en": "City-level accuracy (+/- 10-50 km)"
            }, lang),
            "note": self.translate({
                "ar": "الدقة كافية لاوقات الصلاة (فرق +/- 1-2 دقيقة مقبول)",
                "en": "Accuracy sufficient for prayer times (+/- 1-2 min difference accepted)"
            }, lang)
        }

    async def search(
        self,
        request: Request,
        q: str = Query(..., description="City name in Arabic or English"),
        lang: str = Query("en", description="Language: en or ar"),
        limit: int = Query(5, ge=1, le=10, description="Max results")
    ):
        lang = self.get_lang(request, lang)

        if not q or len(q.strip()) < 2:
            return {
                "error": self.translate({
                    "ar": "اكتب اسم المدينة (حرفان على الأقل)",
                    "en": "Enter city name (at least 2 characters)"
                }, lang)
            }

        # Step 1: Search local DB (fast, offline)
        db_results = self._db_search(q.strip(), limit)

        if db_results:
            cities = []
            for r in db_results:
                cities.append({
                    "name": r["name"],
                    "name_local": r["name_local"],
                    "country": r["country"],
                    "governorate": r["governorate"],
                    "latitude": r["latitude"],
                    "longitude": r["longitude"],
                    "timezone": r["timezone"],
                    "source": "local_db"
                })

            return {
                "query": q,
                "total": len(cities),
                "source": "local_db",
                "results": cities
            }

        # Step 2: Fallback to Nominatim (online)
        self.logger.info(f"City '{q}' not in local DB, falling back to Nominatim")
        nominatim_results = await self._nominatim_search(q, lang, limit)

        if not nominatim_results:
            return {
                "query": q,
                "total": 0,
                "results": [],
                "message": self.translate({
                    "ar": "لم يتم العثور على نتائج",
                    "en": "No results found"
                }, lang)
            }

        return {
            "query": q,
            "total": len(nominatim_results),
            "source": "nominatim",
            "note": self.translate({
                "ar": "النتيجة من OpenStreetMap وتم تخزينها محلياً للاستخدام دون انترنت لاحقاً",
                "en": "Result from OpenStreetMap, cached locally for offline use"
            }, lang),
            "results": nominatim_results
        }

    async def prayer_times_auto(
        self,
        request: Request,
        method: str = Query("EGYPT", description="Calculation method"),
        lang: str = Query("en", description="Language: en or ar"),
        timezone: str = Query(None, description="Override timezone")
    ):
        lang = self.get_lang(request, lang)

        ip = request.headers.get("X-Forwarded-For")
        if ip:
            ip = ip.split(",")[0].strip()
        else:
            ip = request.client.host

        if ip in ("127.0.0.1", "::1", "localhost"):
            return {
                "error": self.translate({
                    "ar": "لا يمكن كشف الموقع من localhost. استخدم /api/v1/prayer-times مع lat/long.",
                    "en": "Cannot detect location from localhost. Use /api/v1/prayer-times with lat/long."
                }, lang)
            }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://ip-api.com/json/{ip}",
                params={"fields": "status,country,city,lat,lon,timezone,query"},
                timeout=5.0
            )
            location = response.json()

        if location.get("status") != "success":
            return {
                "error": self.translate({
                    "ar": "فشل في كشف الموقع تلقائياً",
                    "en": "Failed to auto-detect location"
                }, lang)
            }

        latitude = location.get("lat")
        longitude = location.get("lon")
        detected_timezone = timezone or location.get("timezone", "UTC")
        city = location.get("city")
        country = location.get("country")

        from datetime import datetime
        from modules.prayer_times.module import Module as PrayerModule

        prayer_module = PrayerModule()
        prayer_module.config = self.config
        prayer_module.logger = self.logger

        prayer_data = prayer_module.calculate_times(
            latitude=latitude,
            longitude=longitude,
            timezone=detected_timezone,
            method=method,
            date=datetime.now(),
            lang=lang
        )

        return {
            "detected_location": {
                "ip": location.get("query"),
                "city": city,
                "country": country,
                "latitude": latitude,
                "longitude": longitude,
                "timezone": detected_timezone,
            },
            "accuracy_note": self.translate({
                "ar": "دقة IP: مستوى المدينة. الفرق +/- 1-2 دقيقة مقبول شرعاً كاحتياط.",
                "en": "IP accuracy: city-level. +/- 1-2 min difference is acceptable as a fallback."
            }, lang),
            "prayer_times": prayer_data
        }
