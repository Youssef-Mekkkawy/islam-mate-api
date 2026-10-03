# اسماء الله الحسنى

اسماء الله الحسنى التسعة والتسعون مع معانيها بالعربية والانجليزية.

## نقاط النهاية

### GET /api/v1/allah-names

الحصول على جميع الاسماء الحسنى.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/allah-names"
```

**الرد:**

```json
{
  "total": 99,
  "names": [
    {
      "number": 1,
      "arabic": "الله",
      "transliteration": "Allah",
      "name": "الله",
      "meaning": "المستحق للعبادة وحده"
    },
    {
      "number": 2,
      "arabic": "الرحمن",
      "transliteration": "Ar-Rahman",
      "name": "الرحمن",
      "meaning": "ذو الرحمة الواسعة لجميع الخلق"
    }
  ]
}
```

---

### GET /api/v1/allah-names/{number}

الحصول على اسم بالرقم (1-99).

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/allah-names/1"
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/allah-names/99"
```

---

### GET /api/v1/allah-names/random

الحصول على اسم عشوائي.

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/allah-names/random"
```
