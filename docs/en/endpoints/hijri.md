# Hijri Calendar

## Endpoints

### GET /api/v1/hijri

Get today's Hijri date.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/hijri"
```

**Response:**

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
    "month_name": "Rabi al-Thani",
    "year": 1448
  }
}
```

---

### GET /api/v1/hijri/convert

Convert a Gregorian date to Hijri.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| date | string | Yes | Gregorian date YYYY-MM-DD |
| lang | string | No | Language: en or ar |

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/hijri/convert?date=2026-10-03"
```

---

### GET /api/v1/hijri/months

Get all 12 Hijri month names.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/hijri/months"
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/hijri/months"
```

**Response:**

```json
{
  "months": [
    {"number": 1, "name": "Muharram"},
    {"number": 2, "name": "Safar"},
    {"number": 9, "name": "Ramadan"}
  ]
}
```

---

### GET /api/v1/hijri/events

Get Islamic events for a given year.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/hijri/events?year=2026"
```

**Response:**

```json
{
  "year": 2026,
  "total": 10,
  "events": [
    {
      "name": "Eid al-Fitr",
      "gregorian_date": "2026-03-30",
      "hijri_date": "1447/10/01"
    },
    {
      "name": "Eid al-Adha",
      "gregorian_date": "2026-06-06",
      "hijri_date": "1447/12/10"
    }
  ]
}
```
