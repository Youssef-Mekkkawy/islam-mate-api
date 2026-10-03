# حساب اوقات الصلاة — الرياضيات والنظرية

هذه الصفحة تشرح كيفية حساب اوقات الصلاة رياضياً. مفيد للاستخدام دون انترنت او لفهم كيف يعمل الـ API داخلياً.

---

## لماذا الرياضيات مهمة؟

تطبيق الحساب الرياضي الخالص يعني:

- يعمل **بدون انترنت** تماماً
- لا يعتمد على خادم خارجي
- يعمل على اي جهاز — هاتف، حاسوب، نظام مضمن
- نفس الدقة مع الخدمات الاونلاين

الـ API يستخدم هذه الرياضيات داخلياً.

---

## الشرح المبسط

### كيف تُحسب اوقات الصلاة؟

اوقات الصلاة مبنية على موضع الشمس في السماء. كل صلاة لها تعريف فلكي دقيق:

| الصلاة | التعريف الفلكي |
|---|---|
| **الفجر** | عندما تصل الشمس الى زاوية محددة تحت الافق |
| **الشروق** | لحظة ظهور قرص الشمس فوق الافق |
| **الظهر** | عندما تبلغ الشمس اعلى نقطة في السماء (الزوال) |
| **العصر** | عندما يصبح ظل الشيء مساوياً لطوله + ظله وقت الظهر |
| **المغرب** | غروب الشمس |
| **العشاء** | عندما تختفي الشفق الاحمر |

### لماذا تختلف الاوقات بين الطرق؟

الاختلاف فقط في زاوية الفجر والعشاء:

| الطريقة | زاوية الفجر | زاوية العشاء |
|---|---|---|
| EGYPT | 19.5° | 17.5° |
| MWL | 18° | 17° |
| ISNA | 15° | 15° |
| KARACHI | 18° | 18° |

### العصر — مذهبان

- **الشافعي والجمهور:** الظل = طول الشيء × 1 + ظل الزوال
- **الحنفي:** الظل = طول الشيء × 2 + ظل الزوال

---

## الرياضيات

### الخطوة 1 — التاريخ اليولياني

```python
JD = 367 * Year
   - INT(7 * (Year + INT((Month + 9) / 12)) / 4)
   + INT(275 * Month / 9)
   + Day + 1721013.5
```

### الخطوة 2 — القرن اليولياني

```python
T = (JD - 2451545.0) / 36525.0
```

### الخطوة 3 — موضع الشمس

```python
L0 = 280.46646 + 36000.76983 * T  # الطول الاوسط
M  = 357.52911 + 35999.05029 * T  # الشذوذ الاوسط
```

### الخطوة 4 — الظهر (الزوال)

```python
solar_noon = 12 + timezone_offset - longitude / 15 - equation_of_time / 60
```

### الخطوة 5 — زاوية الساعة للشروق/الغروب

```python
cos(H) = (sin(-0.8333°) - sin(lat) * sin(dec)) / (cos(lat) * cos(dec))
sunrise = solar_noon - H / 15
sunset  = solar_noon + H / 15
```

### الخطوة 6 — الفجر والعشاء

```python
cos(H) = (sin(-angle°) - sin(lat) * sin(dec)) / (cos(lat) * cos(dec))
fajr = solar_noon - H / 15
isha = solar_noon + H / 15
```

### الخطوة 7 — العصر

```python
shadow_ratio = 1  # شافعي
# او
shadow_ratio = 2  # حنفي

target = arctan(1 / (shadow_ratio + tan(|lat - dec|)))
asr = solar_noon + H_asr / 15
```

---

## تطبيق Python

```python
import math
from datetime import datetime
import pytz


class PrayerTimeCalculator:
    METHODS = {
        "EGYPT":   {"fajr": 19.5, "isha": 17.5},
        "MWL":     {"fajr": 18.0, "isha": 17.0},
        "ISNA":    {"fajr": 15.0, "isha": 15.0},
        "KARACHI": {"fajr": 18.0, "isha": 18.0},
    }

    def __init__(self, method="EGYPT", asr_method="shafi"):
        self.method = self.METHODS[method]
        self.asr_shadow = 1 if asr_method == "shafi" else 2

    def calculate(self, latitude, longitude, date=None, timezone="UTC"):
        if date is None:
            date = datetime.now()

        tz = pytz.timezone(timezone)
        offset = tz.utcoffset(date).total_seconds() / 3600

        # ... حساب كامل
        return {
            "date": date.strftime("%Y-%m-%d"),
            "prayers": [
                {"name": "الفجر",    "time": "04:38"},
                {"name": "الشروق",   "time": "06:01"},
                {"name": "الظهر",    "time": "11:51"},
                {"name": "العصر",    "time": "15:14"},
                {"name": "المغرب",   "time": "17:40"},
                {"name": "العشاء",   "time": "19:02"},
            ]
        }


# الاستخدام
calc = PrayerTimeCalculator(method="EGYPT", asr_method="shafi")
result = calc.calculate(latitude=30.04, longitude=31.23, timezone="Africa/Cairo")
for prayer in result["prayers"]:
    print(f"{prayer['name']}: {prayer['time']}")
```

---

## التحقق من النتائج

للتحقق من تطبيقك:

1. احسب اوقات مدينتك
2. قارن مع [Islamic Finder](https://www.islamicfinder.org)
3. استخدم نفس الطريقة (EGYPT, MWL, الخ)
4. الفرق المقبول: **±1-2 دقيقة**

---

## ملخص

| الصلاة | التعريف الفلكي |
|---|---|
| الفجر | الشمس تصل زاوية الفجر تحت الافق الشرقي |
| الظهر | الشمس في خط الزوال المحلي |
| العصر | الظل = (1× او 2×) الارتفاع + ظل الزوال |
| المغرب | غروب الشمس تحت الافق الغربي |
| العشاء | الشمس تصل زاوية العشاء تحت الافق الغربي |

الشيء الوحيد الذي يختلف بين الطرق هو قيم زوايا الفجر والعشاء.
