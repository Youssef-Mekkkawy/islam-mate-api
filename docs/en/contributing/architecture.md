# Architecture

## Project Structure

```
islam-mate-api/
├── kernel/
│   ├── kernel.py           # System boot point
│   ├── router.py           # Route registration
│   ├── module_loader.py    # Module discovery and loading
│   ├── middleware.py       # Auth middleware
│   ├── rate_limiter.py     # Rate limiting
│   └── services/
│       ├── auth.py         # API key system (SQLite)
│       ├── cache.py        # Redis cache
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
│   └── base_module.py      # BaseModule all modules inherit from
├── data/                   # Data files (hosted on HuggingFace)
├── scripts/                # Data download scripts
├── tests/                  # 98 tests
├── docs/                   # This documentation
├── config.yaml             # Module toggles and settings
├── main.py                 # FastAPI app entry point
└── docker-compose.yml
```

## Request Lifecycle

```
HTTP Request
    ↓
Rate Limiter Middleware (60 req/min per IP)
    ↓
Auth Middleware (dev: bypass, prod: key required)
    ↓
FastAPI Router (/api/v1/{lang}/{endpoint})
    ↓
Module Handler
    ↓
JSON Response
```

## BaseModule

Every module inherits from `BaseModule` and gets these for free:

| Property | Type | Description |
|---|---|---|
| `self.translate()` | method | AR/EN translation |
| `self.get_lang()` | method | Detect language from URL |
| `self.logger` | Loguru | Request and error logging |
| `self.config` | ConfigReader | Read config.yaml |
| `self.db` | SQLAlchemy | Database connection |
| `self.cache` | Redis | Cache connection |

## Language Routing

All endpoints support three patterns:

```
/api/v1/prayer-times       # Default (English)
/api/v1/en/prayer-times    # Explicit English
/api/v1/ar/prayer-times    # Arabic
/api/v1/prayer-times?lang=ar  # Query param
```

## Module On/Off

Toggle any module in `config.yaml` without restart:

```yaml
modules:
  prayer_times: true
  azkar: true
  hadith: false  # disabled
```
