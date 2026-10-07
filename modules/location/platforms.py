"""
Islam Mate API — Platform Location Endpoints
Guides developers on how to get location per platform,
plus attempts IP-based detection as a fallback.
"""

from fastapi import APIRouter, Request
from typing import Optional
import httpx

router = APIRouter(prefix="/api/v1/location", tags=["Location — Platforms"])

# ─── helpers ────────────────────────────────────────────────────────────────

async def _try_ip_detect(request: Request) -> dict:
    """Attempt IP-based location detection. Returns result or error dict."""
    client_ip = request.client.host if request.client else None

    if not client_ip or client_ip in ("127.0.0.1", "::1", "localhost"):
        return {
            "detected": False,
            "note": "localhost detected — IP detection requires a real public IP",
        }

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"http://ip-api.com/json/{client_ip}?fields=status,city,lat,lon,timezone,country,regionName"
            )
            data = resp.json()

        if data.get("status") == "success":
            return {
                "detected": True,
                "ip": client_ip,
                "city": data.get("city"),
                "region": data.get("regionName"),
                "country": data.get("country"),
                "latitude": data.get("lat"),
                "longitude": data.get("lon"),
                "timezone": data.get("timezone"),
            }
        return {
            "detected": False,
            "note": "IP detection failed — use city search or manual entry",
        }
    except Exception:
        return {
            "detected": False,
            "note": "IP detection service unreachable — use city search or manual entry",
        }


def _method_list(priority: list[str]) -> list[dict]:
    """Convert priority list to labeled method objects."""
    labels = {
        "gps": {"label_en": "Use my GPS", "label_ar": "استخدم GPS", "requires_permission": True},
        "wifi": {"label_en": "Detect via WiFi", "label_ar": "كشف عبر WiFi", "requires_permission": False},
        "ip_detection": {"label_en": "Auto detect (IP)", "label_ar": "كشف تلقائي", "requires_permission": False},
        "city_search": {"label_en": "Search city", "label_ar": "ابحث عن مدينة", "requires_permission": False},
        "map_picker": {"label_en": "Pick on map", "label_ar": "اختر على الخريطة", "requires_permission": False},
        "manual_entry": {"label_en": "Enter manually", "label_ar": "إدخال يدوي", "requires_permission": False},
    }
    return [
        {"method": m, "order": i + 1, **labels.get(m, {})}
        for i, m in enumerate(priority)
    ]


# ─── /location/android ──────────────────────────────────────────────────────

@router.get("/android")
async def location_android(request: Request):
    """
    Android — location detection guide + IP fallback.

    Returns the recommended method priority for Android apps,
    with a developer guide for each method.
    """
    ip_result = await _try_ip_detect(request)

    priority = ["gps", "wifi", "ip_detection", "city_search", "map_picker"]

    return {
        "platform": "android",
        "ip_detection": ip_result,
        "methods": _method_list(priority),
        "guide": {
            "gps": {
                "title": "GPS (Recommended)",
                "description": "Most accurate. Requires ACCESS_FINE_LOCATION permission.",
                "permission": "android.permission.ACCESS_FINE_LOCATION",
                "code_hint": "Use FusedLocationProviderClient from Google Play Services for best battery + accuracy balance.",
                "flutter_hint": "Use the 'geolocator' package: await Geolocator.getCurrentPosition()",
            },
            "wifi": {
                "title": "WiFi / Network Location",
                "description": "Good accuracy indoors. Uses ACCESS_COARSE_LOCATION.",
                "permission": "android.permission.ACCESS_COARSE_LOCATION",
                "code_hint": "FusedLocationProviderClient with PRIORITY_BALANCED_POWER_ACCURACY.",
                "flutter_hint": "Same geolocator package, lower accuracy setting.",
            },
            "ip_detection": {
                "title": "IP Detection (Automatic Fallback)",
                "description": "No permission needed. Accuracy: city level (~10–50 km).",
                "endpoint": "/api/v1/location/detect",
                "note": "Use when user denies GPS permission.",
            },
            "city_search": {
                "title": "City Search",
                "description": "User types their city name.",
                "endpoint": "/api/v1/location/search?q={city_name}",
                "note": "Use as manual override or when other methods fail.",
            },
            "map_picker": {
                "title": "Map Picker",
                "description": "User taps their location on a map.",
                "endpoint": "/map/picker",
                "embed": "Load in WebView or Flutter WebView. Listen for postMessage with lat/lng.",
            },
        },
        "cache_recommendation": {
            "enabled": True,
            "ttl_hours": 24,
            "note": "Cache the detected location locally to avoid repeated API calls.",
        },
    }


# ─── /location/ios ──────────────────────────────────────────────────────────

@router.get("/ios")
async def location_ios(request: Request):
    """
    iOS — location detection guide + IP fallback.
    """
    ip_result = await _try_ip_detect(request)

    priority = ["gps", "wifi", "ip_detection", "city_search", "map_picker"]

    return {
        "platform": "ios",
        "ip_detection": ip_result,
        "methods": _method_list(priority),
        "guide": {
            "gps": {
                "title": "Core Location GPS (Recommended)",
                "description": "Most accurate. Requires NSLocationWhenInUseUsageDescription in Info.plist.",
                "plist_key": "NSLocationWhenInUseUsageDescription",
                "code_hint": "Use CLLocationManager. Request whenInUseAuthorization before starting updates.",
                "flutter_hint": "Use 'geolocator' package. Add NSLocationWhenInUseUsageDescription to Info.plist.",
            },
            "wifi": {
                "title": "WiFi / Network Location",
                "description": "Uses kCLAuthorizationStatusAuthorizedWhenInUse with lower accuracy.",
                "code_hint": "CLLocationManager with desiredAccuracy = kCLLocationAccuracyKilometer.",
            },
            "ip_detection": {
                "title": "IP Detection (Automatic Fallback)",
                "description": "No permission needed. Accuracy: city level.",
                "endpoint": "/api/v1/location/detect",
                "note": "Use when user denies Core Location permission.",
            },
            "city_search": {
                "title": "City Search",
                "endpoint": "/api/v1/location/search?q={city_name}",
            },
            "map_picker": {
                "title": "Map Picker",
                "endpoint": "/map/picker",
                "embed": "Load in WKWebView. Use window.postMessage to receive lat/lng back.",
            },
        },
        "cache_recommendation": {
            "enabled": True,
            "ttl_hours": 24,
        },
    }


# ─── /location/windows ──────────────────────────────────────────────────────

@router.get("/windows")
async def location_windows(request: Request):
    """
    Windows — location detection guide + IP fallback.
    """
    ip_result = await _try_ip_detect(request)

    priority = ["wifi", "ip_detection", "city_search", "map_picker", "manual_entry"]

    return {
        "platform": "windows",
        "ip_detection": ip_result,
        "methods": _method_list(priority),
        "guide": {
            "wifi": {
                "title": "Windows Location API",
                "description": "Uses WiFi triangulation via Windows.Devices.Geolocation.",
                "code_hint": "Geolocator geolocator = new Geolocator(); var position = await geolocator.GetGeopositionAsync();",
                "note": "User must have Location Services enabled in Windows Settings → Privacy → Location.",
                "python_hint": "Use the 'geocoder' library: geocoder.ip('me') as fallback.",
            },
            "ip_detection": {
                "title": "IP Detection (Primary Fallback)",
                "description": "No permission needed. Accuracy: city level.",
                "endpoint": "/api/v1/location/detect",
                "note": "Most reliable on Windows where GPS is uncommon.",
            },
            "city_search": {
                "title": "City Search",
                "endpoint": "/api/v1/location/search?q={city_name}",
            },
            "map_picker": {
                "title": "Map Picker",
                "endpoint": "/map/picker",
                "embed": "Embed in WebView2 (WPF/WinForms) or Electron BrowserWindow.",
            },
            "manual_entry": {
                "title": "Manual Entry",
                "description": "User types city name or coordinates.",
                "note": "Always offer as last resort.",
            },
        },
        "cache_recommendation": {
            "enabled": True,
            "ttl_hours": 168,
            "note": "Cache for 1 week on desktop — location rarely changes.",
        },
    }


# ─── /location/linux ────────────────────────────────────────────────────────

@router.get("/linux")
async def location_linux(request: Request):
    """
    Linux — location detection guide + IP fallback.
    """
    ip_result = await _try_ip_detect(request)

    priority = ["wifi", "ip_detection", "city_search", "map_picker", "manual_entry"]

    return {
        "platform": "linux",
        "ip_detection": ip_result,
        "methods": _method_list(priority),
        "guide": {
            "wifi": {
                "title": "GeoClue2 (Linux Location Service)",
                "description": "D-Bus service for location on Linux. Available on most modern distros.",
                "command": "apt install geoclue-2.0  # Debian/Ubuntu",
                "python_hint": "Use 'pyclue' or call D-Bus directly via dbus-python.",
                "note": "Not available on all server Linux installs — use IP detection as primary.",
            },
            "ip_detection": {
                "title": "IP Detection (Primary on Linux)",
                "description": "Most reliable option for Linux desktop and server.",
                "endpoint": "/api/v1/location/detect",
                "python_hint": "import geocoder; g = geocoder.ip('me'); print(g.latlng)",
            },
            "city_search": {
                "title": "City Search",
                "endpoint": "/api/v1/location/search?q={city_name}",
            },
            "map_picker": {
                "title": "Map Picker",
                "endpoint": "/map/picker",
                "embed": "Embed in Electron, GTK WebView, or Qt WebEngine.",
            },
            "manual_entry": {
                "title": "Manual Entry",
                "description": "User types city name or lat/long.",
            },
        },
        "cache_recommendation": {
            "enabled": True,
            "ttl_hours": 168,
        },
    }


# ─── /location/web ──────────────────────────────────────────────────────────

@router.get("/web")
async def location_web(request: Request):
    """
    Web / Browser — location detection guide + IP fallback.
    """
    ip_result = await _try_ip_detect(request)

    priority = ["wifi", "gps", "ip_detection", "city_search", "map_picker"]

    return {
        "platform": "web",
        "ip_detection": ip_result,
        "methods": _method_list(priority),
        "guide": {
            "wifi": {
                "title": "Geolocation API (WiFi + GPS)",
                "description": "Built into every modern browser. Uses WiFi or GPS depending on device.",
                "code_hint": """navigator.geolocation.getCurrentPosition(
  (pos) => {
    const lat = pos.coords.latitude;
    const lng = pos.coords.longitude;
    // send to your API
  },
  (err) => {
    // fallback to IP detection
  }
);""",
                "note": "Requires HTTPS. User must grant permission.",
            },
            "gps": {
                "title": "High-Accuracy GPS (Mobile Browser)",
                "description": "Available on mobile browsers with GPS hardware.",
                "code_hint": "navigator.geolocation.getCurrentPosition(cb, err, { enableHighAccuracy: true })",
            },
            "ip_detection": {
                "title": "IP Detection (No-Permission Fallback)",
                "description": "Works immediately, no permission popup.",
                "endpoint": "/api/v1/location/detect",
                "note": "Use when user denies browser location or as initial fast load.",
            },
            "city_search": {
                "title": "City Search",
                "endpoint": "/api/v1/location/search?q={city_name}",
                "note": "Add a search box to your UI calling this endpoint.",
            },
            "map_picker": {
                "title": "Map Picker",
                "endpoint": "/map/picker",
                "embed": "Embed as <iframe>. Listen for window.addEventListener('message', ...) to receive {lat, lng}.",
                "example": """<iframe src="/map/picker?response=full" id="map-picker"></iframe>
<script>
  window.addEventListener('message', (e) => {
    if (e.data.lat && e.data.lng) {
      console.log(e.data); // { lat, lng, city, timezone }
    }
  });
</script>""",
            },
        },
        "cache_recommendation": {
            "enabled": False,
            "note": "Do not cache in browser — sessionStorage only if needed.",
        },
    }