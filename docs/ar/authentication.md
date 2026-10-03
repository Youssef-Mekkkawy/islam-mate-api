# المصادقة

## وضع التطوير

المصادقة معطلة بشكل افتراضي. شغل الخادم واستخدم API مباشرة بدون مفتاح.

---

## وضع الانتاج

### 1. تفعيل المصادقة

في ملف `config.yaml`:

```yaml
app:
  mode: production
security:
  auth_enabled: true
```

### 2. الحصول على مفتاح API

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "اسمك", "email": "email@example.com"}'
```

الرد:

```json
{
  "message": "API key generated successfully",
  "api_key": "im_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "warning": "Save this key - it will not be shown again"
}
```

::: warning تحذير
احفظ المفتاح فور الحصول عليه. لن يظهر مرة اخرى.
:::

### 3. استخدام المفتاح

#### عبر X-API-Key Header

```bash
curl http://localhost:8000/api/v1/hadith/bukhari/1 \
  -H "X-API-Key: im_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

#### عبر Authorization Header

```bash
curl http://localhost:8000/api/v1/hadith/bukhari/1 \
  -H "Authorization: Bearer im_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

#### عبر Query Parameter

```
http://localhost:8000/api/v1/hadith/bukhari/1?api_key=im_xxx
```

---

## رموز الاستجابة

| الرمز | المعنى |
|---|---|
| 200 | ناجح |
| 401 | مفتاح API مطلوب |
| 403 | مفتاح API غير صالح |
| 429 | تجاوزت الحد المسموح |

---

## المسارات المعفاة

لا تحتاج هذه المسارات الى مفتاح حتى في وضع الانتاج:

- `GET /` — الصفحة الرئيسية
- `GET /health` — فحص الصحة
- `GET /docs` — التوثيق التفاعلي
- `POST /api/v1/auth/register` — تسجيل مفتاح جديد
