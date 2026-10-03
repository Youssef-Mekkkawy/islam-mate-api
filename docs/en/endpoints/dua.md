# Dua

Duas are personal supplications. This module provides categorized duas with Arabic text and English translation.

## Endpoints

### GET /api/v1/dua

Get all available Dua categories.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/dua"
```

**Response:**

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

Get all duas in a specific category.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/dua/food"
curl "https://islam-mate-api.readthedocs.io/api/v1/dua/travel"
curl "https://islam-mate-api.readthedocs.io/api/v1/dua/sleep"
```

**Response:**

```json
{
  "category": "food",
  "total": 2,
  "duas": [
    {
      "id": 1,
      "repeat": 1,
      "transliteration": "Bismillah",
      "text": "In the name of Allah",
      "source": "Abu Dawud",
      "description": "Said before eating"
    }
  ]
}
```

---

### GET /api/v1/dua/random

Get a random Dua from any category.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/dua/random"
```

## Language Support

```bash
# English
curl "https://islam-mate-api.readthedocs.io/api/v1/en/dua/food"

# Arabic
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/dua/food"
```
