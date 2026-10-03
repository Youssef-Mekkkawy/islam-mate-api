# Azkar

Azkar (أذكار) are Islamic remembrance phrases from Hisnul Muslim by Sheikh Said bin Wahf al-Qahtani.

## Available Categories

130+ categories including:
- Morning and Evening Azkar
- Sleep Azkar
- Waking Up Azkar
- After Prayer Azkar
- Entering/Leaving Home
- Food Duas
- Travel Duas

## Endpoints

### GET /api/v1/azkar

Get all Azkar categories.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/azkar"
```

**Response:**

```json
{
  "total": 130,
  "categories": [
    {
      "id": 27,
      "slug": "morning_evening",
      "title": "Morning and Evening Azkar",
      "count": 18,
      "audio_url": "https://huggingface.co/..."
    }
  ]
}
```

---

### GET /api/v1/azkar/{category_id}

Get all Azkar in a specific category by ID.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/azkar/27"
```

**Response:**

```json
{
  "id": 27,
  "slug": "morning_evening",
  "title": "Morning and Evening Azkar",
  "audio_url": "https://huggingface.co/...",
  "total": 18,
  "azkar": [
    {
      "id": 75,
      "repeat": 1,
      "text": "I seek refuge in Allah from the accursed devil...",
      "source": "Abu Dawud",
      "audio_url": "https://huggingface.co/..."
    }
  ]
}
```

---

### GET /api/v1/azkar/slug/{slug}

Get Azkar by category slug name.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/azkar/slug/morning_evening"
curl "https://islam-mate-api.readthedocs.io/api/v1/azkar/slug/sleep"
curl "https://islam-mate-api.readthedocs.io/api/v1/azkar/slug/after_prayer"
```

---

### GET /api/v1/azkar/random/item

Get a random Azkar from any category.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/azkar/random/item"
```

**Response:**

```json
{
  "category": "Morning and Evening Azkar",
  "azkar": {
    "id": 75,
    "repeat": 3,
    "text": "SubhanAllah wa bihamdihi...",
    "source": "Bukhari",
    "audio_url": "https://huggingface.co/..."
  }
}
```

## Data Source

All Azkar data is from [Hisnul Muslim](https://hisnmuslim.com) — the official API. Audio files are hosted on HuggingFace.
