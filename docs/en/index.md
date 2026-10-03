# Islam Mate API 🕌

**Open-source Islamic REST API for Muslim developers**

---

## What is Islam Mate API?

A single unified REST API giving Muslim developers access to all essential Islamic data in one place.

No more juggling 5 different APIs. One key, everything Islamic.

---

## Features

| Module | Endpoints | Description |
|---|---|---|
| Prayer Times | 4 | Daily times, next prayer, monthly calendar |
| Qibla | 1 | Direction and distance to Mecca |
| Ramadan | 2 | Suhoor/Iftar times |
| Hijri Calendar | 4 | Conversion, months, Islamic events |
| Azkar | 4 | Morning, evening, sleep, after prayer |
| Dua | 3 | Categorized duas |
| 99 Names of Allah | 3 | Names with AR + EN meanings |
| Hadith | 4 | 8 collections, 36,000+ hadiths |

---

## Quick Start

```bash
git clone https://github.com/Youssef-Mekkkawy/islam-mate-api
cd islam-mate-api
pip install -r requirements.txt
python scripts/fetch_azkar.py
python scripts/fetch_hadith.py
uvicorn main:app --reload
```

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Quick Example

```bash
curl "http://localhost:8000/api/v1/en/prayer-times?latitude=30.04&longitude=31.23&timezone=Africa/Cairo"
curl "http://localhost:8000/api/v1/en/hadith/random"
curl "http://localhost:8000/api/v1/en/allah-names/random"
```
