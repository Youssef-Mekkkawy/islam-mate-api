# الادعية

## نقاط النهاية

### GET /api/v1/dua

الحصول على جميع فئات الادعية.

```bash
curl "http://localhost:8000/api/v1/ar/dua"
```

**الرد:**

```json
{
  "total": 4,
  "categories": [
    {"category": "food", "count": 2},
    {"category": "sleep", "count": 1},
    {"category": "travel", "count": 1},
    {"category": "general", "count": 2}
  ]
}
```

---

### GET /api/v1/dua/{category}

الحصول على ادعية فئة معينة.

```bash
curl "http://localhost:8000/api/v1/ar/dua/food"
curl "http://localhost:8000/api/v1/ar/dua/travel"
curl "http://localhost:8000/api/v1/ar/dua/sleep"
```

**الرد:**

```json
{
  "category": "food",
  "total": 2,
  "duas": [
    {
      "id": 1,
      "repeat": 1,
      "transliteration": "Bismillah",
      "text": "بِسْمِ اللَّهِ",
      "source": "ابو داود",
      "description": "يقال قبل الاكل"
    }
  ]
}
```

---

### GET /api/v1/dua/random

الحصول على دعاء عشوائي.

```bash
curl "http://localhost:8000/api/v1/ar/dua/random"
```
