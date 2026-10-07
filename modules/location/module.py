from fastapi import APIRouter, Query, Request
from base.base_module import BaseModule
import httpx
import sqlite3
import yaml
from pathlib import Path


DB_PATH = Path("data/cities.db")
LOCATION_CONFIG_PATH = Path("config/location.yaml")


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
            "/location/auto",
            self.auto,
            methods=["GET"],
            summary="Smart location detection — GPS coords if provided, IP fallback",
            tags=["Location"]
        )
        router.add_api_route(
            "/location/config",
            self.config_view,
            methods=["GET"],
            summary="Location config — enabled methods and platform priorities",
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

    def _db_reverse_geocode(self, lat: float, lng: float) -> dict | None:
        """Find nearest city in DB for given coordinates (within ~50 km)."""
        if not DB_PATH.exists():
            return None

        try:
            con = sqlite3.connect(DB_PATH)
            con.row_factory = sqlite3.Row

            # Use approximate bounding box (1 degree ≈ 111 km)
            delta = 0.5  # ~55 km search radius
            rows = con.execute("""
                SELECT
                    ci.name,
                    ci.name_local,
                    ci.latitude,
                    ci.longitude,
                    ci.timezone,
                    g.name AS governorate,
                    c.name AS country,
                    c.iso2,
                    (
                        (ci.latitude - ?) * (ci.latitude - ?) +
                        (ci.longitude - ?) * (ci.longitude - ?)
                    ) AS dist_sq
                FROM cities ci
                JOIN governorates g ON g.id = ci.governorate_id
                JOIN countries c ON c.id = g.country_id
                WHERE
                    ci.latitude BETWEEN ? AND ?
                    AND ci.longitude BETWEEN ? AND ?
                ORDER BY dist_sq ASC
                LIMIT 1
            """, (
                lat, lat, lng, lng,
                lat - delta, lat + delta,
                lng - delta, lng + delta
            )).fetchone()

            con.close()
            return dict(rows) if rows else None
        except Exception:
            return None

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
                    (result["country"], result.get("country_code",
                     "XX").upper(), result.get("timezone", "UTC"))
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

    async def _nominatim_reverse(self, lat: float, lng: float, lang: str = "en") -> dict | None:
        """Reverse geocode via Nominatim — lat/lng → city info."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://nominatim.openstreetmap.org/reverse",
                    params={
                        "lat": lat,
                        "lon": lng,
                        "format": "json",
                        "addressdetails": 1,
                        "accept-language": lang,
                    },
                    headers={"User-Agent": "IslamMateAPI/2.0"},
                    timeout=10.0
                )
                r = response.json()

            if "error" in r:
                return None

            address = r.get("address", {})
            city_name = (
                address.get("city") or
                address.get("town") or
                address.get("village") or
                address.get("county") or
                r.get("display_name", "").split(",")[0]
            )

            result = {
                "name": city_name,
                "name_local": None,
                "country": address.get("country", ""),
                "country_code": address.get("country_code", "").upper(),
                "governorate": address.get("state", ""),
                "latitude": lat,
                "longitude": lng,
                "timezone": None,
                "display_name": r.get("display_name", ""),
                "source": "nominatim"
            }

            # Cache for offline use later
            self._cache_to_db(result)
            return result

        except Exception:
            return None

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
                params={
                    "fields": "status,message,country,city,lat,lon,timezone,query"},
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
        self.logger.info(
            f"City '{q}' not in local DB, falling back to Nominatim")
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

    async def auto(
        self,
        request: Request,
        lat: float = Query(
            None, description="Latitude from device GPS (optional)"),
        lng: float = Query(
            None, description="Longitude from device GPS (optional)"),
        platform: str = Query(
            None, description="Platform hint: android, ios, windows, linux, web"),
        lang: str = Query("en", description="Language: en or ar")
    ):
        """
        Smart location detection.

        Priority:
          1. If lat + lng provided → treat as GPS, reverse-geocode from local DB,
             fall back to Nominatim if DB has no nearby city.
          2. Otherwise → detect from client IP via ip-api.com.

        Returns unified location object + method used + accuracy note.
        """
        lang = self.get_lang(request, lang)

        # ── Branch 1: client sent GPS coordinates ──────────────────────────
        if lat is not None and lng is not None:
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                return {
                    "error": self.translate({
                        "ar": "إحداثيات غير صالحة. lat بين -90 و 90، lng بين -180 و 180.",
                        "en": "Invalid coordinates. lat must be -90..90, lng must be -180..180."
                    }, lang)
                }

            # Step 1: reverse-geocode from local DB (fast, offline)
            db_city = self._db_reverse_geocode(lat, lng)

            if db_city:
                return {
                    "method": "gps",
                    "source": "local_db",
                    "latitude": lat,
                    "longitude": lng,
                    "city": db_city.get("name"),
                    "city_local": db_city.get("name_local"),
                    "governorate": db_city.get("governorate"),
                    "country": db_city.get("country"),
                    "country_code": db_city.get("iso2"),
                    "timezone": db_city.get("timezone"),
                    "accuracy": self.translate({
                        "ar": "دقة عالية — إحداثيات GPS من الجهاز",
                        "en": "High accuracy — GPS coordinates from device"
                    }, lang),
                    "platform": platform
                }

            # Step 2: DB miss → Nominatim reverse geocode (online)
            self.logger.info(
                f"No DB city near ({lat}, {lng}), trying Nominatim reverse geocode")
            nom_city = await self._nominatim_reverse(lat, lng, lang)

            if nom_city:
                return {
                    "method": "gps",
                    "source": "nominatim",
                    "latitude": lat,
                    "longitude": lng,
                    "city": nom_city.get("name"),
                    "city_local": nom_city.get("name_local"),
                    "governorate": nom_city.get("governorate"),
                    "country": nom_city.get("country"),
                    "country_code": nom_city.get("country_code"),
                    "timezone": nom_city.get("timezone"),
                    "display_name": nom_city.get("display_name"),
                    "accuracy": self.translate({
                        "ar": "دقة عالية — إحداثيات GPS من الجهاز (اسم المدينة من OpenStreetMap)",
                        "en": "High accuracy — GPS coordinates from device (city name from OpenStreetMap)"
                    }, lang),
                    "note": self.translate({
                        "ar": "تم تخزين المدينة محلياً للاستخدام دون انترنت لاحقاً",
                        "en": "City cached locally for future offline use"
                    }, lang),
                    "platform": platform
                }

            # Step 3: GPS coords provided but city lookup failed entirely
            return {
                "method": "gps",
                "source": "coordinates_only",
                "latitude": lat,
                "longitude": lng,
                "city": None,
                "country": None,
                "timezone": None,
                "accuracy": self.translate({
                    "ar": "إحداثيات GPS متاحة — اسم المدينة غير متاح حالياً",
                    "en": "GPS coordinates available — city name unavailable right now"
                }, lang),
                "note": self.translate({
                    "ar": "يمكن حساب أوقات الصلاة مباشرة من الإحداثيات",
                    "en": "Prayer times can be calculated directly from coordinates"
                }, lang),
                "platform": platform
            }

        # ── Branch 2: no GPS — detect from IP ─────────────────────────────
        ip = request.headers.get("X-Forwarded-For")
        if ip:
            ip = ip.split(",")[0].strip()
        else:
            ip = request.client.host

        if ip in ("127.0.0.1", "::1", "localhost"):
            return {
                "method": "none",
                "source": "localhost",
                "latitude": None,
                "longitude": None,
                "city": None,
                "country": None,
                "timezone": None,
                "error": self.translate({
                    "ar": "الكشف التلقائي غير متاح من localhost. أرسل lat و lng من الجهاز.",
                    "en": "Auto-detection unavailable from localhost. Pass lat and lng from device."
                }, lang),
                "platform": platform,
                "suggested_endpoint": self.translate({
                    "ar": "/api/v1/location/auto?lat=30.0444&lng=31.2357",
                    "en": "/api/v1/location/auto?lat=30.0444&lng=31.2357"
                }, lang)
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://ip-api.com/json/{ip}",
                    params={
                        "fields": "status,message,country,countryCode,regionName,city,lat,lon,timezone,query"},
                    timeout=5.0
                )
                data = response.json()
        except Exception:
            return {
                "method": "none",
                "source": "ip_failed",
                "error": self.translate({
                    "ar": "فشل في الكشف عن الموقع. أرسل lat و lng يدوياً.",
                    "en": "Location detection failed. Pass lat and lng manually."
                }, lang),
                "platform": platform
            }

        if data.get("status") != "success":
            return {
                "method": "none",
                "source": "ip_failed",
                "error": self.translate({
                    "ar": "فشل في الكشف عن الموقع عبر IP",
                    "en": "Failed to detect location from IP"
                }, lang),
                "message": data.get("message", "Unknown error"),
                "platform": platform
            }

        return {
            "method": "ip",
            "source": "ip-api",
            "ip": data.get("query"),
            "latitude": data.get("lat"),
            "longitude": data.get("lon"),
            "city": data.get("city"),
            "governorate": data.get("regionName"),
            "country": data.get("country"),
            "country_code": data.get("countryCode"),
            "timezone": data.get("timezone"),
            "accuracy": self.translate({
                "ar": "دقة مستوى المدينة (+/- 10-50 كم)",
                "en": "City-level accuracy (+/- 10-50 km)"
            }, lang),
            "note": self.translate({
                "ar": "دقة كافية لأوقات الصلاة (فرق +/- 1-2 دقيقة مقبول شرعاً). للدقة الكاملة أرسل GPS.",
                "en": "Sufficient for prayer times (+/- 1-2 min accepted). Send GPS coords for full accuracy."
            }, lang),
            "platform": platform
        }

    async def config_view(
        self,
        request: Request,
        platform: str = Query(
            None, description="Filter to a specific platform: android, ios, windows, linux, web, desktop"),
        lang: str = Query("en", description="Language: en or ar")
    ):
        """
        Return the active location config from config/location.yaml.

        Protection level is controlled by config_endpoint.protection:
          - public     → anyone can call it
          - api_key    → requires valid X-API-Key (enforced by main middleware)
          - disabled   → 404

        This endpoint only reads and exposes the config — it never modifies it.
        """
        lang = self.get_lang(request, lang)

        # Load YAML
        if not LOCATION_CONFIG_PATH.exists():
            return {
                "error": self.translate({
                    "ar": "ملف الإعدادات غير موجود",
                    "en": "Config file not found"
                }, lang),
                "path": str(LOCATION_CONFIG_PATH)
            }

        try:
            with open(LOCATION_CONFIG_PATH, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
        except Exception as e:
            return {
                "error": self.translate({
                    "ar": "فشل في قراءة ملف الإعدادات",
                    "en": "Failed to read config file"
                }, lang),
                "detail": str(e)
            }

        loc = raw.get("location", {})

        # Check if this endpoint is disabled in config
        endpoint_cfg = loc.get("config_endpoint", {})
        if not endpoint_cfg.get("enabled", True):
            return {
                "error": self.translate({
                    "ar": "نقطة الإعدادات معطلة",
                    "en": "Config endpoint is disabled"
                }, lang)
            }

        # Build method list with labels
        methods_raw = loc.get("methods", {})
        methods = {}
        for key, val in methods_raw.items():
            methods[key] = {
                "enabled": val.get("enabled", False),
                "label": self.translate({
                    "en": val.get("label_en", key),
                    "ar": val.get("label_ar", key)
                }, lang),
            }
            # Include extra fields (excluding label_en/label_ar to keep response clean)
            for extra_key in ("provider", "timeout_seconds", "source", "cache_results",
                              "default_zoom", "default_center_lat", "default_center_lng",
                              "online_tiles", "offline_tiles", "allow_coordinates", "allow_city_name"):
                if extra_key in val:
                    methods[key][extra_key] = val[extra_key]

        # Platform priorities
        platforms_raw = loc.get("platforms", {})

        if platform:
            # Filter to requested platform
            if platform not in platforms_raw:
                return {
                    "error": self.translate({
                        "ar": f"المنصة '{platform}' غير معرّفة في الإعدادات",
                        "en": f"Platform '{platform}' is not defined in config"
                    }, lang),
                    "available_platforms": list(platforms_raw.keys())
                }

            plat_cfg = platforms_raw[platform]
            priority_labeled = [
                {
                    "method": m,
                    "order": i + 1,
                    "label": methods.get(m, {}).get("label", m),
                    "enabled": methods.get(m, {}).get("enabled", False)
                }
                for i, m in enumerate(plat_cfg.get("priority", []))
            ]

            return {
                "platform": platform,
                "priority": priority_labeled,
                "cache_location": plat_cfg.get("cache_location", False),
                "cache_ttl_hours": plat_cfg.get("cache_ttl_hours"),
                "methods": methods,
                "global": {
                    "enabled": loc.get("enabled", True),
                    "on_method_disabled": loc.get("on_method_disabled", "skip"),
                    "accuracy": loc.get("accuracy", {}),
                    "offline": loc.get("offline", {}),
                }
            }

        # Return all platforms
        platforms_out = {}
        for plat_name, plat_cfg in platforms_raw.items():
            priority_labeled = [
                {
                    "method": m,
                    "order": i + 1,
                    "label": methods.get(m, {}).get("label", m),
                    "enabled": methods.get(m, {}).get("enabled", False)
                }
                for i, m in enumerate(plat_cfg.get("priority", []))
            ]
            platforms_out[plat_name] = {
                "priority": priority_labeled,
                "cache_location": plat_cfg.get("cache_location", False),
                "cache_ttl_hours": plat_cfg.get("cache_ttl_hours"),
            }

        return {
            "enabled": loc.get("enabled", True),
            "on_method_disabled": loc.get("on_method_disabled", "skip"),
            "methods": methods,
            "platforms": platforms_out,
            "accuracy": loc.get("accuracy", {}),
            "offline": loc.get("offline", {}),
            "map": loc.get("map", {}),
        }

    async def prayer_times_auto(
        self,
        request: Request,
        method: str = Query("EGYPT", description="Calculation method"),
        lang: str = Query("en", description="Language: en or ar"),
        timezone: str = Query(None, description="Override timezone")
    ):
        import pytz as _pytz
        from datetime import date as _date
        from modules.prayer_times.core.methods import PrayerTimes, CalculationMethod, AsrMethod

        lang = self.get_lang(request, lang)

        ip = request.headers.get("X-Forwarded-For")
        if ip:
            ip = ip.split(",")[0].strip()
        else:
            ip = request.client.host

        # Localhost fallback: use Cairo for testing
        if ip in ("127.0.0.1", "::1", "localhost"):
            latitude, longitude = 30.0444, 31.2357
            detected_timezone = timezone or "Africa/Cairo"
            city, country = "Cairo (localhost fallback)", "Egypt"
            ip_used = ip
        else:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://ip-api.com/json/{ip}",
                    params={"fields": "status,country,city,lat,lon,timezone,query"},
                    timeout=5.0
                )
                location = response.json()

            if location.get("status") != "success":
                from fastapi import HTTPException
                raise HTTPException(503, self.translate({
                    "ar": "فشل في كشف الموقع تلقائياً",
                    "en": "Failed to auto-detect location"
                }, lang))

            latitude = location["lat"]
            longitude = location["lon"]
            detected_timezone = timezone or location.get("timezone", "UTC")
            city = location.get("city")
            country = location.get("country")
            ip_used = location.get("query", ip)

        # Calculate prayer times directly via core
        today = _date.today()
        tz = _pytz.timezone(detected_timezone)
        try:
            pt = PrayerTimes(CalculationMethod[method], AsrMethod.STANDARD)
            times = pt.calc_times(today, tz, longitude, latitude)
        except KeyError:
            from fastapi import HTTPException
            raise HTTPException(400, f"Invalid method: {method}")
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(500, str(e))

        return {
            "detected_location": {
                "ip": ip_used,
                "city": city,
                "country": country,
                "latitude": latitude,
                "longitude": longitude,
                "timezone": detected_timezone,
            },
            "date": today.isoformat(),
            "method": method,
            "accuracy_note": self.translate({
                "ar": "دقة IP: مستوى المدينة. الفرق +/- 1-2 دقيقة مقبول شرعاً كاحتياط.",
                "en": "IP accuracy: city-level. +/- 1-2 min difference is acceptable as a fallback."
            }, lang),
            "sunrise": times["sunrise"].strftime("%H:%M"),
            "prayers": [
                {"name": self.translate({"en": "Fajr",    "ar": "الفجر"},    lang), "time": times["fajr"].strftime("%H:%M")},
                {"name": self.translate({"en": "Dhuhr",   "ar": "الظهر"},   lang), "time": times["dhuhr"].strftime("%H:%M")},
                {"name": self.translate({"en": "Asr",     "ar": "العصر"},     lang), "time": times["asr"].strftime("%H:%M")},
                {"name": self.translate({"en": "Maghrib", "ar": "المغرب"}, lang), "time": times["maghrib"].strftime("%H:%M")},
                {"name": self.translate({"en": "Isha",    "ar": "العشاء"},    lang), "time": times["isha"].strftime("%H:%M")},
            ]
        }
