# تحديد المعدل

## الحد الافتراضي

- **60 طلب في الدقيقة** لكل عنوان IP
- يُعاد ضبط العداد كل 60 ثانية

---

## تجاوز الحد

عند تجاوز الحد تحصل على:

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Limit: 60 per minute",
  "retry_after": "60 seconds"
}
```

برمز الاستجابة: **429 Too Many Requests**

---

## الضبط في config.yaml

```yaml
security:
  rate_limiting: true
```

لتعطيل تحديد المعدل في التطوير:

```yaml
security:
  rate_limiting: false
```

---

## المسارات المعفاة

المسارات الثابتة مثل `/docs` و `/health` معفاة من تحديد المعدل.

---

## نصيحة

احفظ نتائج الاستعلامات محلياً عند الامكان. اوقات الصلاة لا تتغير خلال اليوم — لا داعي لطلبها اكثر من مرة.
