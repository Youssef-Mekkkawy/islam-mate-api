# الحديث النبوي

## المجموعات المتاحة

| الكود | الاسم | عدد الاحاديث |
|---|---|---|
| bukhari | صحيح البخاري | 7,589 |
| muslim | صحيح مسلم | 7,563 |
| abudawud | سنن ابي داود | 5,274 |
| tirmidhi | جامع الترمذي | 3,998 |
| ibnmajah | سنن ابن ماجه | 4,343 |
| nasai | سنن النسائي | 5,765 |
| malik | موطأ مالك | 1,858 |
| nawawi40 | الاربعون النووية | 42 |

**المجموع: 36,432 حديث**

---

## نقاط النهاية

### GET /api/v1/hadith

الحصول على قائمة المجموعات.

```bash
curl "http://localhost:8000/api/v1/ar/hadith"
```

---

### GET /api/v1/hadith/{collection}

الحصول على احاديث مجموعة مع دعم الصفحات.

| المعامل | الوصف |
|---|---|
| page | رقم الصفحة (افتراضي: 1) |
| limit | عدد النتائج (افتراضي: 50، الحد: 200) |

```bash
curl "http://localhost:8000/api/v1/ar/hadith/bukhari?page=1&limit=10"
```

---

### GET /api/v1/hadith/{collection}/{number}

الحصول على حديث بالرقم.

```bash
curl "http://localhost:8000/api/v1/ar/hadith/bukhari/1"
```

**الرد:**

```json
{
  "collection": "bukhari",
  "hadith": {
    "number": 1,
    "grade": "",
    "text": "حَدَّثَنَا الْحُمَيْدِيُّ...",
    "reference": {
      "book": "Sahih al Bukhari",
      "hadith_number": 1
    }
  }
}
```

---

### GET /api/v1/hadith/random

الحصول على حديث عشوائي.

```bash
# من اي مجموعة
curl "http://localhost:8000/api/v1/ar/hadith/random"

# من مجموعة محددة
curl "http://localhost:8000/api/v1/ar/hadith/random?collection=nawawi40"
```

---

## مصدر البيانات

[fawazahmed0/hadith-api](https://github.com/fawazahmed0/hadith-api) — رخصة Unlicense (ملك عام).
