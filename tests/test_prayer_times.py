import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestPrayerTimes:

    def test_get_prayer_times_success(self):
        response = client.get(
            "/api/v1/prayer-times",
            params={"latitude": 30.0444, "longitude": 31.2357}
        )
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "location" in data
        assert "prayers" in data
        assert len(data["prayers"]) == 5

    def test_get_prayer_times_arabic(self):
        response = client.get(
            "/api/v1/prayer-times",
            params={"latitude": 30.0444, "longitude": 31.2357, "lang": "ar"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["prayers"][0]["name"] == "الفجر"

    def test_get_prayer_times_english(self):
        response = client.get(
            "/api/v1/prayer-times",
            params={"latitude": 30.0444, "longitude": 31.2357, "lang": "en"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["prayers"][0]["name"] == "Fajr"

    def test_get_prayer_times_all_methods(self):
        methods = ["EGYPT", "MWL", "ISNA", "KARACHI"]
        for method in methods:
            response = client.get(
                "/api/v1/prayer-times",
                params={"latitude": 30.0444, "longitude": 31.2357, "method": method}
            )
            assert response.status_code == 200, f"Method {method} failed"

    def test_get_prayer_times_invalid_method(self):
        response = client.get(
            "/api/v1/prayer-times",
            params={"latitude": 30.0444, "longitude": 31.2357, "method": "INVALID"}
        )
        assert response.status_code == 400

    def test_get_prayer_times_invalid_latitude(self):
        response = client.get(
            "/api/v1/prayer-times",
            params={"latitude": 999, "longitude": 31.2357}
        )
        assert response.status_code == 422

    def test_get_prayer_times_invalid_date(self):
        response = client.get(
            "/api/v1/prayer-times",
            params={"latitude": 30.0444, "longitude": 31.2357, "date": "invalid-date"}
        )
        assert response.status_code == 400

    def test_get_prayer_times_with_date(self):
        response = client.get(
            "/api/v1/prayer-times",
            params={"latitude": 30.0444, "longitude": 31.2357, "date": "2026-01-01"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == "2026-01-01"

    def test_get_next_prayer(self):
        response = client.get(
            "/api/v1/prayer/next",
            params={"latitude": 30.0444, "longitude": 31.2357}
        )
        assert response.status_code == 200
        data = response.json()
        assert "next_prayer" in data
        assert "time" in data

    def test_get_prayer_month(self):
        response = client.get(
            "/api/v1/prayer/month",
            params={"latitude": 30.0444, "longitude": 31.2357, "month": 1, "year": 2026}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["month"] == 1
        assert data["year"] == 2026
        assert len(data["days"]) == 31

    def test_get_prayer_methods(self):
        response = client.get("/api/v1/prayer/methods")
        assert response.status_code == 200
        data = response.json()
        assert len(data["methods"]) == 7

    def test_prayer_times_response_structure(self):
        response = client.get(
            "/api/v1/prayer-times",
            params={"latitude": 30.0444, "longitude": 31.2357}
        )
        data = response.json()
        assert "sunrise" in data
        assert "timezone" in data
        assert "method" in data
        prayer_names = [p["name"] for p in data["prayers"]]
        assert len(prayer_names) == 5
