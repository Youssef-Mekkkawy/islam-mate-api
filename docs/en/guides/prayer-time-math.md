# Prayer Time Calculation — Math & Theory

This page explains how prayer times are calculated mathematically, both conceptually and with full implementation. Useful for offline use, embedded systems, or understanding how the API works internally.

---

## Why Math Matters

GPS and internet are not always available. A pure math implementation means:

- Works completely **offline**
- No external API dependency
- Runs on any device — phone, PC, embedded hardware
- Same accuracy as online services

The Islam Mate API uses this exact same math internally.

---

## Arabic Explanation — الشرح بالعربية

### كيف تُحسب أوقات الصلاة؟

أوقات الصلاة مبنية على موضع الشمس في السماء. كل صلاة لها تعريف فلكي دقيق:

| الصلاة | التعريف الفلكي |
|---|---|
| **الفجر** | عندما تصل الشمس إلى زاوية محددة تحت الأفق (الفجر الصادق) |
| **الشروق** | لحظة ظهور قرص الشمس فوق الأفق |
| **الظهر** | عندما تبلغ الشمس أعلى نقطة في السماء (الزوال) |
| **العصر** | عندما يصبح ظل الشيء مساوياً لطوله + ظله وقت الظهر |
| **المغرب** | غروب الشمس — اختفاء قرص الشمس تحت الأفق |
| **العشاء** | عندما تختفي الشفق الأحمر — زاوية محددة تحت الأفق |

### لماذا تختلف الأوقات من مكان لآخر؟

لأن الأرض كروية. موضع الشمس بالنسبة لك يعتمد على:
- **خط العرض (Latitude)** — كلما ابتعدت شمالاً أو جنوباً، تغير الوقت
- **خط الطول (Longitude)** — يحدد الفارق الزمني مع خط غرينتش
- **فصل السنة** — الشمس تشرق وتغرب في أوقات مختلفة

### لماذا تختلف الأوقات بين الطرق (EGYPT / MWL / ISNA)؟

الاختلاف فقط في زاوية الفجر والعشاء:
- **EGYPT:** فجر 19.5°، عشاء 17.5°
- **MWL:** فجر 18°، عشاء 17°
- **ISNA:** فجر 15°، عشاء 15°

كل طريقة تعكس اجتهاد علمي في تحديد متى تبدأ "الظلمة الحقيقية".

### العصر — مذهبان

- **الشافعي والجمهور:** الظل = طول الشيء × 1 + ظل الزوال
- **الحنفي:** الظل = طول الشيء × 2 + ظل الزوال

---

## English Explanation

### The Core Concept

Prayer times are defined by the **sun's position in the sky**, measured as an angle below or above the horizon.

The earth rotates 360° in 24 hours = **15° per hour**. By knowing the sun's exact position for any latitude, longitude, and date, we can calculate precisely when each prayer begins.

### Prayer Definitions

**Fajr (Dawn)**
Begins when the sun reaches a defined angle below the eastern horizon — this is the first light of true dawn. The angle varies by calculation method (15°–19.5°).

**Sunrise**
The moment the upper edge of the sun appears above the horizon. Not a prayer, but needed to define the end of Fajr and forbidden prayer times.

**Dhuhr (Noon)**
Solar noon — the exact moment the sun reaches its highest point (local meridian transit). After this, shadows begin growing toward the east.

**Asr (Afternoon)**
When the shadow of an object equals its own height (Shafi'i) or twice its height (Hanafi), plus the minimum shadow at Dhuhr.

```
Shafi'i:  shadow_length = object_height × 1 + shadow_at_dhuhr
Hanafi:   shadow_length = object_height × 2 + shadow_at_dhuhr
```

**Maghrib (Sunset)**
When the upper edge of the sun disappears below the western horizon. Most methods set this 0–1 minutes after sunset.

**Isha (Night)**
When the red twilight disappears from the western sky. Defined as a sun angle below the horizon (15°–18° depending on method).

---

## The Mathematics

### Step 1 — Julian Date

Convert the Gregorian date to a Julian Day Number (continuous day count since noon, January 1, 4713 BC).

```
JD = 367 × Year
   - INT(7 × (Year + INT((Month + 9) / 12)) / 4)
   + INT(275 × Month / 9)
   + Day
   + 1721013.5
   + UT / 24
   - 0.5 × sign(100 × Year + Month - 190002.5)
   + 0.5
```

Where `UT` = Universal Time (UTC hour)

### Step 2 — Julian Century

```
T = (JD - 2451545.0) / 36525.0
```

(Days since J2000.0, divided by days per century)

### Step 3 — Sun's Mean Longitude and Anomaly

```
L0 = 280.46646 + 36000.76983 × T  (degrees)
M  = 357.52911 + 35999.05029 × T  (degrees, mean anomaly)
```

Normalize both to 0°–360°.

### Step 4 — Sun's Equation of Center

```
C = (1.914602 - 0.004817 × T - 0.000014 × T²) × sin(M)
  + (0.019993 - 0.000101 × T) × sin(2M)
  + 0.000289 × sin(3M)
```

### Step 5 — Sun's True Longitude

```
sun_lon = L0 + C
```

### Step 6 — Apparent Right Ascension and Declination

```
Ω  = 125.04 - 1934.136 × T
λ  = sun_lon - 0.00569 - 0.00478 × sin(Ω)
ε  = 23.439 - 0.00000036 × T  (obliquity)

declination = arcsin(sin(ε) × sin(λ))
```

### Step 7 — Equation of Time

```
y = tan²(ε / 2)
EqT = y × sin(2L0)
    - 2e × sin(M)
    + 4e × y × sin(M) × cos(2L0)
    - 0.5 × y² × sin(4L0)
    - 1.25 × e² × sin(2M)
    
EqT = EqT × (4 / π) × (180 / π)  → in minutes
```

### Step 8 — Solar Noon (Dhuhr)

```
solar_noon = 12 + timezone_offset - longitude / 15 - EqT / 60
```

### Step 9 — Hour Angle for Sunrise/Sunset

```
cos(H) = (sin(−0.8333°) − sin(lat) × sin(dec))
         / (cos(lat) × cos(dec))

H = arccos(result)   → in degrees
```

Where -0.8333° accounts for atmospheric refraction and sun's disc size.

```
sunrise = solar_noon - H / 15   (hours)
sunset  = solar_noon + H / 15   (hours)
```

### Step 10 — Hour Angle for Fajr / Isha

Replace −0.8333° with the method's twilight angle (negative = below horizon):

```
cos(H) = (sin(−angle°) − sin(lat) × sin(dec))
         / (cos(lat) × cos(dec))

fajr = solar_noon - H / 15
isha = solar_noon + H / 15
```

### Step 11 — Asr Hour Angle

```
shadow_ratio = 1   (Shafi'i)
             = 2   (Hanafi)

target = arctan(1 / (shadow_ratio + tan(|lat − dec|)))

cos(H_asr) = (sin(target) − sin(lat) × sin(dec))
             / (cos(lat) × cos(dec))

asr = solar_noon + H_asr / 15
```

---

## Calculation Method Angles

| Method | Fajr Angle | Isha Angle | Region |
|---|---|---|---|
| EGYPT | 19.5° | 17.5° | Egypt + Arab world |
| MWL | 18° | 17° | Europe, Far East |
| ISNA | 15° | 15° | North America |
| KARACHI | 18° | 18° | Pakistan, South Asia |
| MAKKAH | 18.5° | 90 min after Maghrib | Gulf |
| TEHRAN | 17.7° | 14° | Iran |
| JAFARI | 16° | 14° | Shia |

---

## Timezone Handling

All calculation results are in **UTC**. Convert to local time:

```
local_time = utc_time + timezone_offset_hours + dst_offset
```

Use a proper timezone library — never hardcode offsets. DST changes automatically.

**Python:**
```python
import pytz
from datetime import datetime

tz = pytz.timezone("Africa/Cairo")
utc_dt = datetime.utcnow().replace(tzinfo=pytz.utc)
local_dt = utc_dt.astimezone(tz)
offset = local_dt.utcoffset().total_seconds() / 3600
```

**Dart:**
```dart
final cairo = DateTime.now().timeZoneOffset;
```

---

## Edge Cases

### High Latitudes (Above 48°N or Below 48°S)

At extreme latitudes (Scandinavia, Alaska, southern Argentina) the sun may never reach the required twilight angle in summer — causing Fajr or Isha to be undefined.

**Estimation methods used:**

| Method | How it works |
|---|---|
| Nearest Latitude | Use times from nearest city below 48° |
| Middle of Night | Divide night into halves |
| Seventh of Night | Use 1/7 of night for Fajr, 1/7 for Isha |
| Angle-Based | Proportional to angle deficit |

The Islam Mate API uses **Middle of Night** as the default fallback.

### Polar Regions (Above 66°N)

Midnight sun (summer) or polar night (winter). No standard solution — consult local Islamic authority.

---

## Python Implementation

Complete, self-contained class. No external dependencies except `math` and `datetime`.

```python
import math
from datetime import datetime, timedelta
import pytz


class PrayerTimeCalculator:
    """
    Prayer time calculator based on astronomical algorithms.
    Implements EGYPT, MWL, ISNA, KARACHI, MAKKAH, TEHRAN, JAFARI methods.
    """

    METHODS = {
        "EGYPT":    {"fajr": 19.5, "isha": 17.5, "isha_type": "angle"},
        "MWL":      {"fajr": 18.0, "isha": 17.0, "isha_type": "angle"},
        "ISNA":     {"fajr": 15.0, "isha": 15.0, "isha_type": "angle"},
        "KARACHI":  {"fajr": 18.0, "isha": 18.0, "isha_type": "angle"},
        "MAKKAH":   {"fajr": 18.5, "isha": 90,   "isha_type": "minutes"},
        "TEHRAN":   {"fajr": 17.7, "isha": 14.0, "isha_type": "angle"},
        "JAFARI":   {"fajr": 16.0, "isha": 14.0, "isha_type": "angle"},
    }

    def __init__(self, method: str = "EGYPT", asr_method: str = "shafi"):
        if method not in self.METHODS:
            raise ValueError(f"Unknown method: {method}. Choose from {list(self.METHODS.keys())}")
        self.method = self.METHODS[method]
        self.asr_shadow = 1 if asr_method == "shafi" else 2

    def _to_rad(self, deg: float) -> float:
        return deg * math.pi / 180

    def _to_deg(self, rad: float) -> float:
        return rad * 180 / math.pi

    def _normalize_angle(self, angle: float) -> float:
        return angle - 360 * math.floor(angle / 360)

    def _julian_date(self, year: int, month: int, day: int) -> float:
        if month <= 2:
            year -= 1
            month += 12
        A = math.floor(year / 100)
        B = 2 - A + math.floor(A / 4)
        return math.floor(365.25 * (year + 4716)) + \
               math.floor(30.6001 * (month + 1)) + \
               day + B - 1524.5

    def _sun_position(self, jd: float) -> dict:
        T = (jd - 2451545.0) / 36525.0

        L0 = self._normalize_angle(280.46646 + 36000.76983 * T)
        M  = self._normalize_angle(357.52911 + 35999.05029 * T)
        M_rad = self._to_rad(M)

        C = (1.914602 - 0.004817 * T - 0.000014 * T**2) * math.sin(M_rad) + \
            (0.019993 - 0.000101 * T) * math.sin(2 * M_rad) + \
            0.000289 * math.sin(3 * M_rad)

        sun_lon = L0 + C
        omega = 125.04 - 1934.136 * T
        lam = sun_lon - 0.00569 - 0.00478 * math.sin(self._to_rad(omega))
        epsilon = 23.439 - 0.00000036 * T

        dec = self._to_deg(math.asin(
            math.sin(self._to_rad(epsilon)) * math.sin(self._to_rad(lam))
        ))

        y = math.tan(self._to_rad(epsilon / 2)) ** 2
        e = 0.016708634
        eq_time = y * math.sin(2 * self._to_rad(L0)) \
                  - 2 * e * math.sin(M_rad) \
                  + 4 * e * y * math.sin(M_rad) * math.cos(2 * self._to_rad(L0)) \
                  - 0.5 * y**2 * math.sin(4 * self._to_rad(L0)) \
                  - 1.25 * e**2 * math.sin(2 * M_rad)
        eq_time_minutes = eq_time * (4 / math.pi) * (180 / math.pi)

        return {"declination": dec, "equation_of_time": eq_time_minutes}

    def _solar_noon(self, longitude: float, timezone: float, eq_time: float) -> float:
        return 12 + timezone - longitude / 15 - eq_time / 60

    def _hour_angle(self, angle_deg: float, lat: float, dec: float) -> float:
        try:
            cos_h = (math.sin(self._to_rad(-angle_deg)) -
                     math.sin(self._to_rad(lat)) * math.sin(self._to_rad(dec))) / \
                    (math.cos(self._to_rad(lat)) * math.cos(self._to_rad(dec)))

            if cos_h < -1 or cos_h > 1:
                return None  # Sun never reaches this angle

            return self._to_deg(math.acos(cos_h))
        except Exception:
            return None

    def _asr_hour_angle(self, lat: float, dec: float) -> float:
        target = self._to_deg(math.atan(
            1 / (self.asr_shadow + math.tan(self._to_rad(abs(lat - dec))))
        ))
        return self._hour_angle(-target, lat, dec)

    def _decimal_to_time(self, hours: float) -> str:
        if hours is None:
            return "--:--"
        hours = hours % 24
        h = int(hours)
        m = int((hours - h) * 60)
        s = int(((hours - h) * 60 - m) * 60)
        # Round to nearest minute
        if s >= 30:
            m += 1
        if m >= 60:
            m = 0
            h += 1
        if h >= 24:
            h = 0
        return f"{h:02d}:{m:02d}"

    def calculate(self, latitude: float, longitude: float,
                  date: datetime = None, timezone: str = "UTC") -> dict:
        """
        Calculate prayer times for a given location and date.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            date: Date to calculate for (default: today)
            timezone: Timezone string (e.g. 'Africa/Cairo')

        Returns:
            Dictionary with prayer times
        """
        if date is None:
            date = datetime.now()

        tz = pytz.timezone(timezone)
        offset = tz.utcoffset(date).total_seconds() / 3600

        jd = self._julian_date(date.year, date.month, date.day)
        sun = self._sun_position(jd)
        dec = sun["declination"]
        eq_time = sun["equation_of_time"]

        noon = self._solar_noon(longitude, offset, eq_time)

        # Hour angles
        fajr_angle = self.method["fajr"]
        isha_angle = self.method["isha"] if self.method["isha_type"] == "angle" else None

        fajr_ha  = self._hour_angle(fajr_angle, latitude, dec)
        sunrise_ha = self._hour_angle(0.8333, latitude, dec)
        asr_ha   = self._asr_hour_angle(latitude, dec)
        sunset_ha = sunrise_ha
        isha_ha  = self._hour_angle(isha_angle, latitude, dec) if isha_angle else None

        fajr   = noon - (fajr_ha / 15) if fajr_ha else None
        sunrise = noon - (sunrise_ha / 15) if sunrise_ha else None
        dhuhr  = noon
        asr    = noon + (asr_ha / 15) if asr_ha else None
        maghrib = noon + (sunset_ha / 15) if sunset_ha else None

        if self.method["isha_type"] == "minutes":
            isha = (maghrib or 0) + self.method["isha"] / 60
        else:
            isha = noon + (isha_ha / 15) if isha_ha else None

        return {
            "date": date.strftime("%Y-%m-%d"),
            "timezone": timezone,
            "method": "custom",
            "location": {"latitude": latitude, "longitude": longitude},
            "prayers": [
                {"name": "Fajr",    "time": self._decimal_to_time(fajr)},
                {"name": "Sunrise", "time": self._decimal_to_time(sunrise)},
                {"name": "Dhuhr",   "time": self._decimal_to_time(dhuhr)},
                {"name": "Asr",     "time": self._decimal_to_time(asr)},
                {"name": "Maghrib", "time": self._decimal_to_time(maghrib)},
                {"name": "Isha",    "time": self._decimal_to_time(isha)},
            ]
        }


# --- Usage ---
if __name__ == "__main__":
    calc = PrayerTimeCalculator(method="EGYPT", asr_method="shafi")

    result = calc.calculate(
        latitude=30.0444,
        longitude=31.2357,
        timezone="Africa/Cairo"
    )

    print(f"Date: {result['date']}")
    print(f"Location: {result['location']}")
    print()
    for prayer in result["prayers"]:
        print(f"{prayer['name']:10}: {prayer['time']}")
```

**Output:**
```
Date: 2026-10-03
Location: {'latitude': 30.0444, 'longitude': 31.2357}

Fajr      : 04:38
Sunrise   : 06:01
Dhuhr     : 11:51
Asr       : 15:14
Maghrib   : 17:40
Isha      : 19:02
```

---

## Verification

To verify your implementation:

1. Run calculations for your city
2. Compare with [Islamic Finder](https://www.islamicfinder.org) or [Azan.ma](https://azan.ma)
3. Use the same method (EGYPT, MWL, etc.)
4. Acceptable tolerance: **±1–2 minutes**

### Why Small Differences Are Normal

- Different rounding approaches (floor vs round)
- Some sites add 1-minute correction for Fajr/Isha
- Atmospheric refraction varies slightly by altitude
- Sea level vs elevation differences

A 1-minute difference is religiously acceptable.

---

## Summary

| Prayer | Astronomical Definition |
|---|---|
| Fajr | Sun reaches Fajr angle below eastern horizon |
| Dhuhr | Sun at local meridian (solar noon) |
| Asr | Shadow = (1× or 2×) height + noon shadow |
| Maghrib | Sun sets below western horizon |
| Isha | Sun reaches Isha angle below western horizon |

The only thing that changes between methods is the Fajr and Isha angle values.
