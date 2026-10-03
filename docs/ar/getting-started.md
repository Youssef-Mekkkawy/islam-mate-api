# البداية السريعة

## المتطلبات

- Python 3.10+
- Git
- Docker (اختياري)

## التثبيت

### 1. استنساخ المشروع

```bash
git clone https://github.com/Youssef-Mekkkawy/islam-mate-api
cd islam-mate-api
```

### 2. إنشاء البيئة الافتراضية

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. تثبيت المكتبات

```bash
pip install -r requirements.txt
```

### 4. إعداد ملف البيئة

```bash
cp .env.example .env
```

### 5. تحميل البيانات

```bash
python scripts/fetch_azkar.py
python scripts/fetch_hadith.py
```

### 6. تشغيل الخادم

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

افتح الواجهة التفاعلية: [https://islam-mate-api.readthedocs.io](https://islam-mate-api.readthedocs.io)

---

## التشغيل باستخدام Docker

```bash
docker compose up
```

---

## التحقق من التثبيت

```bash
curl https://islam-mate-api.readthedocs.io/health
```

الرد المتوقع:

```json
{"status": "ok"}
```

---

## هيكل المشروع

```
islam-mate-api/
├── kernel/          # النواة الاساسية
├── modules/         # وحدات الميزات الاسلامية
├── base/            # الفئة الاساسية للوحدات
├── data/            # ملفات البيانات
├── scripts/         # سكريبتات تحميل البيانات
├── tests/           # 98 اختبار
├── config.yaml      # اعدادات الوحدات
└── main.py          # نقطة دخول التطبيق
```

---

## الخطوة التالية

- [المصادقة](authentication) — كيفية الحصول على مفتاح API
- [نقاط النهاية](endpoints/prayer-times) — استكشاف جميع نقاط النهاية
