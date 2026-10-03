# الاذكار

الاذكار من حصن المسلم للشيخ سعيد بن وهف القحطاني.

## الفئات المتاحة

اكثر من 130 فئة تشمل:
- اذكار الصباح والمساء
- اذكار النوم
- اذكار الاستيقاظ
- الاذكار بعد الصلاة
- دعاء دخول وخروج المنزل
- دعاء الطعام
- دعاء السفر

## نقاط النهاية

### GET /api/v1/azkar

الحصول على جميع فئات الاذكار.

```bash
curl "http://localhost:8000/api/v1/ar/azkar"
```

**الرد:**

```json
{
  "total": 130,
  "categories": [
    {
      "id": 27,
      "slug": "morning_evening",
      "title": "اذكار الصباح والمساء",
      "count": 18,
      "audio_url": "https://huggingface.co/..."
    }
  ]
}
```

---

### GET /api/v1/azkar/{category_id}

الحصول على اذكار فئة معينة برقمها.

```bash
curl "http://localhost:8000/api/v1/ar/azkar/27"
```

---

### GET /api/v1/azkar/slug/{slug}

الحصول على اذكار فئة معينة باسمها.

```bash
curl "http://localhost:8000/api/v1/ar/azkar/slug/morning_evening"
curl "http://localhost:8000/api/v1/ar/azkar/slug/sleep"
curl "http://localhost:8000/api/v1/ar/azkar/slug/after_prayer"
```

**الرد:**

```json
{
  "id": 27,
  "slug": "morning_evening",
  "title": "اذكار الصباح والمساء",
  "total": 18,
  "azkar": [
    {
      "id": 75,
      "repeat": 1,
      "text": "أَعُوذُ بِاللَّهِ مِنَ الشَّيطَانِ الرَّجِيمِ...",
      "source": "ابو داود",
      "audio_url": "https://huggingface.co/..."
    }
  ]
}
```

---

### GET /api/v1/azkar/random/item

الحصول على ذكر عشوائي.

```bash
curl "http://localhost:8000/api/v1/ar/azkar/random/item"
```

---

## مصدر البيانات

جميع بيانات الاذكار من [حصن المسلم](https://hisnmuslim.com) — الواجهة البرمجية الرسمية. ملفات الصوت مستضافة على HuggingFace.
