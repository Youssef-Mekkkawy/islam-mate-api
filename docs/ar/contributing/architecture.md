# هيكل المشروع

```
islam-mate-api/
├── kernel/
│   ├── kernel.py           # نقطة تحميل النظام
│   ├── router.py           # تسجيل المسارات
│   ├── module_loader.py    # تحميل الوحدات
│   ├── middleware.py       # المصادقة
│   ├── rate_limiter.py     # تحديد المعدل
│   └── services/
│       ├── auth.py         # نظام المفاتيح
│       ├── cache.py        # Redis
│       ├── database.py     # PostgreSQL
│       ├── logger.py       # Loguru
│       └── config_reader.py
├── modules/
│   ├── prayer_times/
│   ├── qibla/
│   ├── ramadan/
│   ├── hijri/
│   ├── azkar/
│   ├── dua/
│   ├── allah_names/
│   ├── hadith/
│   └── auth/
├── base/
│   └── base_module.py      # الفئة الاساسية
├── data/                   # البيانات (HuggingFace)
├── scripts/                # سكريبتات التحميل
├── tests/                  # الاختبارات
├── docs/                   # التوثيق
├── config.yaml
├── main.py
└── docker-compose.yml
```

## دورة حياة الطلب

```
HTTP Request
    ↓
Rate Limiter (60 طلب/دقيقة لكل IP)
    ↓
Auth Middleware (dev: bypass, prod: مفتاح مطلوب)
    ↓
FastAPI Router (/api/v1/{lang}/{endpoint})
    ↓
Module Handler
    ↓
JSON Response
```

## BaseModule

كل وحدة ترث من BaseModule وتحصل على:

| الخاصية | النوع | الوصف |
|---|---|---|
| `self.translate()` | method | ترجمة AR/EN |
| `self.get_lang()` | method | كشف اللغة من URL |
| `self.logger` | Loguru | تسجيل الطلبات والاخطاء |
| `self.config` | ConfigReader | قراءة config.yaml |
| `self.db` | SQLAlchemy | اتصال قاعدة البيانات |
| `self.cache` | Redis | اتصال Redis |

## التوجيه بالغة

جميع نقاط النهاية تدعم ثلاثة انماط:

```
/api/v1/prayer-times       # افتراضي (انجليزي)
/api/v1/en/prayer-times    # انجليزي صريح
/api/v1/ar/prayer-times    # عربي
/api/v1/prayer-times?lang=ar  # معامل استعلام
```
