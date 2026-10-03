# اوقات الصلاة

## نقاط النهاية

### GET /api/v1/prayer-times

الحصول على اوقات الصلاة لليوم.

**المعاملات:**

| المعامل | النوع | مطلوب | الوصف |
|---|---|---|---|
| latitude | float | نعم | خط العرض (-90 الى 90) |
| longitude | float | نعم | خط الطول (-180 الى 180) |
| timezone | string | لا | المنطقة الزمنية (افتراضي: UTC) |
| method | string | لا | طريقة الحساب (افتراضي: EGYPT) |
| date | string | لا | التاريخ YYYY-MM-DD (افتراضي: اليوم) |
| lang | string | لا | اللغة: ar او en |

**مثال:**

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/prayer-times?latitude=30.04&longitude=31.23&timezone=Africa/Cairo&method=EGYPT"
```

**الرد:**

```json
{
  "date": "2026-10-03",
  "location": {
    "latitude": 30.04,
    "longitude": 31.23
  },
  "method": "EGYPT",
  "timezone": "Africa/Cairo",
  "sunrise": "06:01",
  "prayers": [
    {"name": "الفجر", "time": "04:38"},
    {"name": "الظهر", "time": "11:51"},
    {"name": "العصر", "time": "15:14"},
    {"name": "المغرب", "time": "17:40"},
    {"name": "العشاء", "time": "19:02"}
  ]
}
```

---

### GET /api/v1/prayer/next

الحصول على الصلاة القادمة.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/prayer/next?latitude=30.04&longitude=31.23&timezone=Africa/Cairo"
```

---

### GET /api/v1/prayer/month

الحصول على اوقات الصلاة لشهر كامل.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/prayer/month?latitude=30.04&longitude=31.23&month=10&year=2026"
```

---

### GET /api/v1/prayer/methods

الحصول على جميع طرق الحساب المتاحة.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/prayer/methods"
```

---

## طرق الحساب

| الكود | الاسم | المنطقة |
|---|---|---|
| EGYPT | الهيئة المصرية | مصر والدول العربية |
| MWL | رابطة العالم الاسلامي | اوروبا |
| ISNA | ISNA | امريكا الشمالية |
| KARACHI | جامعة كراتشي | باكستان وجنوب آسيا |
| MAKKAH | ام القرى | الخليج العربي |
| TEHRAN | معهد طهران | ايران |
| JAFARI | الجعفري | المذهب الجعفري |
