# Running Tests

## Run All Tests

```bash
pytest tests/ -v
```

## Run Specific Module Tests

```bash
pytest tests/test_prayer_times.py -v
pytest tests/test_hadith.py -v
pytest tests/test_azkar.py -v
```

## Run With Coverage

```bash
pip install pytest-cov
pytest tests/ --cov=modules --cov-report=html
```

## Current Test Suite

| File | Tests | Status |
|---|---|---|
| test_prayer_times.py | 12 | ✅ |
| test_qibla.py | 9 | ✅ |
| test_ramadan.py | 9 | ✅ |
| test_hijri.py | 13 | ✅ |
| test_azkar.py | 14 | ✅ |
| test_dua.py | 12 | ✅ |
| test_allah_names.py | 13 | ✅ |
| test_hadith.py | 16 | ✅ |
| **Total** | **98** | ✅ |

## Test Structure

All tests follow the same pattern:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestModuleName:

    def test_basic_endpoint(self):
        response = client.get("/api/v1/endpoint")
        assert response.status_code == 200

    def test_arabic_endpoint(self):
        response = client.get("/api/v1/ar/endpoint")
        assert response.status_code == 200

    def test_english_endpoint(self):
        response = client.get("/api/v1/en/endpoint")
        assert response.status_code == 200

    def test_invalid_input(self):
        response = client.get("/api/v1/endpoint?invalid=true")
        assert response.status_code in [400, 422]

    def test_not_found(self):
        response = client.get("/api/v1/endpoint/99999")
        assert response.status_code == 404
```

## Adding New Tests

When adding a new module, create `tests/test_{module_name}.py` with at minimum:

1. Basic endpoint test
2. Arabic language test
3. English language test
4. Invalid input test
5. Not found test
