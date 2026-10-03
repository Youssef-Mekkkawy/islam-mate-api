# التقويم الهجري

## نقاط النهاية

### GET /api/v1/hijri

الحصول على التاريخ الهجري لليوم.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/hijri"
```

**الرد:**

```json
{
  "gregorian": {
    "date": "2026-10-03",
    "day": 3,
    "month": 10,
    "year": 2026
  },
  "hijri": {
    "date": "1448/04/09",
    "day": 9,
    "month": 4,
    "month_name": "ربيع الثاني",
    "year": 1448
  }
}
```

---

### GET /api/v1/hijri/convert

تحويل تاريخ ميلادي الى هجري.

**المعاملات:**

| المعامل | النوع | مطلوب | الوصف |
|---|---|---|---|
| date | string | نعم | التاريخ الميلادي YYYY-MM-DD |
| lang | string | لا | ar او en |

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/hijri/convert?date=2026-10-03"
```

---

### GET /api/v1/hijri/months

الحصول على اسماء الاشهر الهجرية الاثني عشر.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/hijri/months"
```

**الرد:**

```json
{
  "months": [
    {"number": 1, "name": "محرم"},
    {"number": 2, "name": "صفر"},
    {"number": 9, "name": "رمضان"}
  ]
}
```

---

### GET /api/v1/hijri/events

الحصول على المناسبات الاسلامية لسنة معينة.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/hijri/events?year=2026"
```

**الرد:**

```json
{
  "year": 2026,
  "total": 10,
  "events": [
    {
      "name": "عيد الفطر",
      "gregorian_date": "2026-03-30",
      "hijri_date": "1447/10/01"
    },
    {
      "name": "عيد الاضحى",
      "gregorian_date": "2026-06-06",
      "hijri_date": "1447/12/10"
    }
  ]
}
```
