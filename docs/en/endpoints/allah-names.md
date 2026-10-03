# 99 Names of Allah

The 99 names (Asma ul-Husna) of Allah with meanings in Arabic and English.

## Endpoints

### GET /api/v1/allah-names

Get all 99 names of Allah.

```bash
curl "http://localhost:8000/api/v1/allah-names"
```

**Response:**

```json
{
  "total": 99,
  "names": [
    {
      "number": 1,
      "arabic": "الله",
      "transliteration": "Allah",
      "name": "Allah",
      "meaning": "The One deserving all worship"
    },
    {
      "number": 2,
      "arabic": "الرحمن",
      "transliteration": "Ar-Rahman",
      "name": "The Most Gracious",
      "meaning": "The One who has plenty of mercy for all creation"
    }
  ]
}
```

---

### GET /api/v1/allah-names/{number}

Get a specific name by its number (1-99).

```bash
curl "http://localhost:8000/api/v1/allah-names/1"
curl "http://localhost:8000/api/v1/allah-names/99"
```

**Response:**

```json
{
  "number": 1,
  "arabic": "الله",
  "transliteration": "Allah",
  "name": "Allah",
  "meaning": "The One deserving all worship"
}
```

---

### GET /api/v1/allah-names/random

Get a random name from the 99 names.

```bash
curl "http://localhost:8000/api/v1/allah-names/random"
curl "http://localhost:8000/api/v1/ar/allah-names/random"
```

## Language Support

```bash
# English
curl "http://localhost:8000/api/v1/en/allah-names/1"

# Arabic
curl "http://localhost:8000/api/v1/ar/allah-names/1"
```
