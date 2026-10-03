# Getting Started

## Requirements

- Python 3.10+
- Git
- Docker (optional)

---

## Installation

### 1. Clone the project

```bash
git clone https://github.com/Youssef-Mekkkawy/islam-mate-api
cd islam-mate-api
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup environment

```bash
cp .env.example .env
```

### 5. Download data

```bash
python scripts/fetch_azkar.py
python scripts/fetch_hadith.py
```

### 6. Run the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Docker

```bash
docker compose up
```

---

## Verify installation

```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```
