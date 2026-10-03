# تشغيل الاختبارات

## تشغيل جميع الاختبارات

```bash
pytest tests/ -v
```

## تشغيل اختبارات وحدة معينة

```bash
pytest tests/test_prayer_times.py -v
pytest tests/test_hadith.py -v
```

## الاختبارات الحالية

| الملف | عدد الاختبارات | الحالة |
|---|---|---|
| test_prayer_times.py | 12 | ✅ |
| test_qibla.py | 9 | ✅ |
| test_ramadan.py | 9 | ✅ |
| test_hijri.py | 13 | ✅ |
| test_azkar.py | 14 | ✅ |
| test_dua.py | 12 | ✅ |
| test_allah_names.py | 13 | ✅ |
| test_hadith.py | 16 | ✅ |
| **المجموع** | **98** | ✅ |

## هيكل الاختبارات

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

    def test_not_found(self):
        response = client.get("/api/v1/endpoint/99999")
        assert response.status_code == 404
```
