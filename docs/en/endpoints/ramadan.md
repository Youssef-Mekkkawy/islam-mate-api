# Ramadan

## Endpoints

### GET /api/v1/ramadan

Get Ramadan information and Suhoor/Iftar times for a given year.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| latitude | float | Yes | Latitude |
| longitude | float | Yes | Longitude |
| year | int | No | Year (default: current year) |
| timezone | string | No | Timezone (default: UTC) |
| method | string | No | Calculation method |

```bash
curl "http://localhost:8000/api/v1/ramadan?latitude=30.04&longitude=31.23&year=2026&timezone=Africa/Cairo"
```

---

### GET /api/v1/ramadan/calendar

Get the full Ramadan calendar (all 30 days).

```bash
curl "http://localhost:8000/api/v1/ramadan/calendar?latitude=30.04&longitude=31.23&year=2026&timezone=Africa/Cairo"
```

**Response:**

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
    },
    {
      "day": 2,
      "date": "2026-03-01",
      "hijri_date": "1447/09/02",
      "suhoor": "04:44",
      "iftar": "17:39"
    }
  ]
}
```

## Notes

- Suhoor ends at Fajr time
- Iftar begins at Maghrib time
- Calculation method affects Fajr/Maghrib times
