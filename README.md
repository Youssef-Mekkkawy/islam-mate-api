# Islam Mate API

Open-source REST API for Muslim developers.

Prayer times, Quran, Hadith, Azkar, Dua, Qibla, and 50+ Islamic features — all in one place.

## Features

- Prayer times (7 calculation methods)
- Qibla direction with real math
- Quran (coming soon)
- Hadith (coming soon)
- Azkar (coming soon)
- Dual language: Arabic + English

## Quick Start

### Requirements
- Python 3.10+
- PostgreSQL
- Redis

### Install

\\\ash
git clone https://github.com/Youssef-Mekkkawy/islam-mate-api.git
cd islam-mate-api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
\\\

### Configure

Copy \.env.example\ to \.env\ and update your database settings.

### Run

\\\ash
uvicorn main:app --reload
\\\

### Docs

Open http://localhost:8000/docs

## License

MIT
