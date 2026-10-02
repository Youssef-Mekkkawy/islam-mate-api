# Islam Mate API 🕌

<div align="center">

**Open-source Islamic REST API for Muslim developers**

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-teal.svg)
![Tests](https://img.shields.io/badge/Tests-98%20passing-brightgreen.svg)

[HuggingFace Dataset](https://huggingface.co/datasets/elprofessorai/islam-mate-data) • [GitHub](https://github.com/Youssef-Mekkkawy/islam-mate-api)

</div>

---

## What is Islam Mate API?

A single unified REST API that gives Muslim developers access to all essential Islamic data — prayer times, Quran, Hadith, Azkar, and more — in one place.

No more juggling 5 different APIs. One key, everything Islamic.

---

## Features

| Module | Endpoints | Description |
|---|---|---|
| 🕐 Prayer Times | 4 | Daily times, next prayer, monthly calendar, methods |
| 🧭 Qibla | 1 | Direction and distance to Mecca |
| 🌙 Ramadan | 2 | Suhoor/Iftar times and calendar |
| 📅 Hijri Calendar | 4 | Conversion, months, Islamic events |
| 📿 Azkar | 4 | Morning, evening, sleep, after prayer |
| 🤲 Dua | 3 | Duas by category |
| ✨ 99 Names of Allah | 3 | Names with meanings AR + EN |
| 📖 Hadith | 4 | 8 collections, 36,000+ hadiths |

---

## Quick Start

### Requirements

- Python 3.10+
- Git

### Installation

```bash
git clone https://github.com/Youssef-Mekkkawy/islam-mate-api
cd islam-mate-api
python -m venv venv
source venv/bin/activate
# Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Setup

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
QURAN_CLIENT_ID=your_client_id
QURAN_CLIENT_SECRET=your_client_secret
```

### Download Data

```bash
python scripts/fetch_azkar.py
python scripts/fetch_hadith.py
```

### Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open docs: http://localhost:8000/docs

---

## Docker

```bash
docker compose up
```

> Docker support coming soon.

---

## API Usage

### Language Support

All endpoints support Arabic and English via URL prefix:

```
/api/v1/en/prayer-times?latitude=30.04&longitude=31.23
/api/v1/ar/prayer-times?latitude=30.04&longitude=31.23
```

Or via query param:

```
/api/v1/prayer-times?latitude=30.04&longitude=31.23&lang=ar
```

### Endpoints

#### Prayer Times

```
GET /api/v1/prayer-times?latitude=30.04&longitude=31.23&timezone=Africa/Cairo
GET /api/v1/prayer/next?latitude=30.04&longitude=31.23
GET /api/v1/prayer/month?latitude=30.04&longitude=31.23&month=1&year=2026
GET /api/v1/prayer/methods
```

#### Qibla

```
GET /api/v1/qibla?latitude=30.04&longitude=31.23
```

#### Hijri Calendar

```
GET /api/v1/hijri
GET /api/v1/hijri/convert?date=2026-01-01
GET /api/v1/hijri/months
GET /api/v1/hijri/events?year=2026
```

#### Ramadan

```
GET /api/v1/ramadan?latitude=30.04&longitude=31.23&year=2026
GET /api/v1/ramadan/calendar?latitude=30.04&longitude=31.23&year=2026
```

#### Azkar

```
GET /api/v1/azkar
GET /api/v1/azkar/{category_id}
GET /api/v1/azkar/slug/{slug}
GET /api/v1/azkar/random/item
```

#### Dua

```
GET /api/v1/dua
GET /api/v1/dua/{category}
GET /api/v1/dua/random
```

#### 99 Names of Allah

```
GET /api/v1/allah-names
GET /api/v1/allah-names/{number}
GET /api/v1/allah-names/random
```

#### Hadith

```
GET /api/v1/hadith
GET /api/v1/hadith/{collection}
GET /api/v1/hadith/{collection}/{number}
GET /api/v1/hadith/random
```

Available collections: `bukhari` `muslim` `abudawud` `tirmidhi` `ibnmajah` `nasai` `malik` `nawawi40`

---

## Authentication

### Development Mode

Auth is disabled by default. Just run and use.

### Production Mode

Enable in `config.yaml`:

```yaml
app:
  mode: production
security:
  auth_enabled: true
```

Register for an API key:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Your Name", "email": "your@email.com"}'
```

Use your key:

```bash
curl http://localhost:8000/api/v1/hadith/bukhari/1 \
  -H "X-API-Key: your_key_here"
```

---

## Rate Limiting

- 60 requests per minute per IP
- Returns `429 Too Many Requests` when exceeded
- Configurable in `config.yaml`

---

## Configuration

`config.yaml` controls everything:

```yaml
app:
  mode: development  # development | production

modules:
  prayer_times: true
  azkar: true
  hadith: true
  # toggle any module on/off

security:
  auth_enabled: false
  rate_limiting: true
```

---

## Architecture

```
islam-mate-api/
├── kernel/          # Core: boot, routing, services
├── modules/         # Each Islamic feature as a module
├── base/            # BaseModule all modules inherit from
├── data/            # Local data files (hosted on HuggingFace)
├── scripts/         # Data download scripts
├── tests/           # 98 tests
├── config.yaml      # Module toggles and settings
└── main.py          # FastAPI app entry point
```

---

## Tech Stack

- **Python** + **FastAPI** — REST API
- **SQLite** — API key storage
- **SlowAPI** — Rate limiting
- **HuggingFace** — Audio and data hosting
- **hijridate** — Hijri calendar calculations

---

## Data Sources

| Data | Source | License |
|---|---|---|
| Azkar + Dua | [Hisnul Muslim](https://hisnmuslim.com) | Official API |
| Hadith | [fawazahmed0/hadith-api](https://github.com/fawazahmed0/hadith-api) | Unlicense (Public Domain) |
| Prayer Times | Mathematical calculation | — |
| Quran Metadata | [QUL by Tarteel](https://qul.tarteel.ai) | MIT |
| Al-Sharaawi Lectures | [HuggingFace Dataset](https://huggingface.co/datasets/elprofessorai/islam-mate-data) | — |

---

## Credits

- Quran data: [QUL — Quranic Universal Library](https://qul.tarteel.ai) by Tarteel AI (MIT License)
- Hadith data: [fawazahmed0/hadith-api](https://github.com/fawazahmed0/hadith-api) (Unlicense)
- Azkar + Dua data: [Hisnul Muslim](https://hisnmuslim.com) official API

---

## License

MIT License — free to use, modify, and distribute.

---

<div align="center">
Made with ❤️ for the Muslim developer community
</div>
