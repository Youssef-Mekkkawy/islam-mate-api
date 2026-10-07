<div align="center">

<img src="https://raw.githubusercontent.com/islam-mate/api/main/.github/assets/logo.png" alt="Islam Mate API" width="120" />

# Islam Mate API

**Open-source Islamic REST API — 50+ features, dual language (AR/EN)**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![HuggingFace](https://img.shields.io/badge/Dataset-HuggingFace-orange.svg)](https://huggingface.co/datasets/elprofessorai/islam-mate-data)

[Documentation](#documentation) · [Features](#features) · [Quick Start](#quick-start) · [API Reference](#api-reference) · [Contributing](#contributing)

</div>

---

## What is Islam Mate API?

Islam Mate API is a **self-hosted**, open-source REST API that provides Islamic data and tools for developers. Built with **FastAPI** and a modular **Kernel architecture**, it is designed to be fast, extensible, and easy to deploy.

All large datasets (videos, audio, images) are stored on [HuggingFace](https://huggingface.co/datasets/elprofessorai/islam-mate-data) — no heavy storage required on your server.

---

## Features

| Module | Endpoints | Status |
|---|---|---|
| 🕌 **Prayer Times** | Times, Qibla direction, nearest mosque | ✅ Ready |
| 📖 **Quran** | Surahs, Ayahs, translations, audio | 🚧 In Progress |
| 📚 **Tafseer** | Verse-by-verse tafseer (multiple sources) | 🚧 In Progress |
| 🎙️ **Al-Sharaawi** | 1,032 video episodes from archive.org | ✅ Data Ready |
| 📿 **Dhikr** | Morning/evening adhkar, categories | 🔜 Planned |
| 🌙 **Hijri Calendar** | Date conversion, Islamic events | 🔜 Planned |
| 🕋 **Hajj & Umrah** | Step-by-step guides, duas | 🔜 Planned |
| 💬 **Hadith** | Authenticated hadith by topic/narrator | 🔜 Planned |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Git

### 1. Clone the repo

```bash
git clone https://github.com/islam-mate/api.git
cd api
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your values
```

### 4. Run the API

```bash
python main.py
```

API will be live at: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

---

## API Reference

Base URL: `http://localhost:8000/api/v1`

### Example: Get all Surahs

```http
GET /api/v1/quran/surahs
```

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name_arabic": "الفاتحة",
      "name_english": "Al-Fatiha",
      "revelation_place": "mecca",
      "ayahs_count": 7
    }
  ]
}
```

### Example: Get Ayah with translation

```http
GET /api/v1/quran/ayahs/1?translation=en
```

Full API docs → [docs.islam-mate.com](https://github.com/islam-mate/docs) *(coming soon)*

---

## Project Structure

```
api/
├── main.py                  # FastAPI app entry point
├── kernel/                  # Core framework
│   ├── core/
│   │   ├── app.py           # App factory
│   │   ├── router.py        # Auto-register module routers
│   │   └── database.py      # DB connection
│   ├── services/
│   │   ├── config_reader.py # YAML + .env config loader
│   │   └── module_loader.py # Dynamic module discovery
│   └── middleware/
├── modules/                 # Feature modules
│   ├── quran/
│   │   ├── models.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── tafseer/
│   ├── prayer_times/
│   └── ...
├── config/
│   └── config.yaml          # Main config file
├── .env.example             # Environment variable template
└── requirements.txt
```

---

## Dataset

Large files (videos, audio) are hosted on HuggingFace:

**[elprofessorai/islam-mate-data](https://huggingface.co/datasets/elprofessorai/islam-mate-data)**

```
islam-mate-data/
├── alsharaawi/
│   ├── videos/mkv/          # 1,032 MKV episodes (~298 GB)
│   └── thumbnails/          # GIF thumbnails
└── quran/
    ├── audio/               # Recitations (Mishary, Sudais, ...)
    └── tafseer/             # Tafseer JSON files
```

---

## Documentation

| Resource | Link |
|---|---|
| Interactive API Docs | `http://localhost:8000/docs` (Swagger UI) |
| Project Docs | [github.com/islam-mate/docs](https://github.com/islam-mate/docs) |
| Colab Scripts | [github.com/islam-mate/data](https://github.com/islam-mate/data) |
| HuggingFace Dataset | [huggingface.co/datasets/elprofessorai/islam-mate-data](https://huggingface.co/datasets/elprofessorai/islam-mate-data) |

---

## Contributing

We welcome contributions from the community.

```bash
# 1. Fork the repo
# 2. Create your feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes and commit
git commit -m "feat: add your feature"

# 4. Push to development branch
git push origin feature/your-feature-name

# 5. Open a Pull Request → target: development branch
```

**Rules:**
- All PRs target the `development` branch — never `main`
- Follow the existing module structure
- Include docstrings for all routes
- Test your endpoints before opening PR

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for full guidelines.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Made with ❤️ for the Muslim developer community

⭐ Star this repo if it helped you

</div>
