# رمضان

## نقاط النهاية

### GET /api/v1/ramadan

الحصول على اوقات السحور والافطار لرمضان.

**المعاملات:**

| المعامل | النوع | مطلوب | الوصف |
|---|---|---|---|
| latitude | float | نعم | خط العرض |
| longitude | float | نعم | خط الطول |
| year | int | لا | السنة الميلادية |
| timezone | string | لا | المنطقة الزمنية |
| method | string | لا | طريقة الحساب |

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/ramadan?latitude=30.04&longitude=31.23&year=2026&timezone=Africa/Cairo"
```

---

### GET /api/v1/ramadan/calendar

الحصول على تقويم رمضان كامل (30 يوم).

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/ramadan/calendar?latitude=30.04&longitude=31.23&year=2026&timezone=Africa/Cairo"
```

**الرد:**

```json
{
  "year": 2026,
  "total_days": 30,
  "days": [
    {
      "day": 1,
      "date": "2026-02-28",
      "hijri_date": "1447/09/01",
      "suhoor": "04:45",
      "iftar": "17:38"
    }
  ]
}
```

---

## ملاحظات

- السحور ينتهي عند وقت الفجر
- الافطار يبدأ عند وقت المغرب
- طريقة الحساب تؤثر على اوقات الفجر والمغرب
