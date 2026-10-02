import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestRamadan:

    def test_get_ramadan_times_success(self):
        response = client.get(
            "/api/v1/ramadan",
            params={"latitude": 30.0444, "longitude": 31.2357}
        )
        assert response.status_code == 200
        data = response.json()
        assert "hijri_year" in data
        assert "ramadan" in data
        assert "first_day" in data
        assert "last_day" in data

    def test_ramadan_total_days(self):
        response = client.get(
            "/api/v1/ramadan",
            params={"latitude": 30.0444, "longitude": 31.2357}
        )
        data = response.json()
        total = data["ramadan"]["total_days"]
        assert 29 <= total <= 30

    def test_ramadan_has_suhoor_and_iftar(self):
        response = client.get(
            "/api/v1/ramadan",
            params={"latitude": 30.0444, "longitude": 31.2357}
        )
        data = response.json()
        assert "suhoor_time" in data["first_day"]
        assert "iftar_time" in data["first_day"]

    def test_ramadan_specific_year(self):
        response = client.get(
            "/api/v1/ramadan",
            params={"latitude": 30.0444, "longitude": 31.2357, "year": 1446}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["hijri_year"] == 1446

    def test_ramadan_arabic(self):
        response = client.get(
            "/api/v1/ramadan",
            params={"latitude": 30.0444, "longitude": 31.2357, "lang": "ar"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "السحور" in data["first_day"]["suhoor"]
        assert "الإفطار" in data["first_day"]["iftar"]

    def test_ramadan_calendar_success(self):
        response = client.get(
            "/api/v1/ramadan/calendar",
            params={"latitude": 30.0444, "longitude": 31.2357, "year": 1446}
        )
        assert response.status_code == 200
        data = response.json()
        assert "calendar" in data
        assert "total_days" in data
        assert 29 <= data["total_days"] <= 30

    def test_ramadan_calendar_structure(self):
        response = client.get(
            "/api/v1/ramadan/calendar",
            params={"latitude": 30.0444, "longitude": 31.2357, "year": 1446}
        )
        data = response.json()
        first = data["calendar"][0]
        assert "day" in first
        assert "date" in first
        assert "suhoor" in first
        assert "iftar" in first
        assert "fajr" in first
        assert "dhuhr" in first
        assert "asr" in first
        assert "isha" in first

    def test_ramadan_invalid_latitude(self):
        response = client.get(
            "/api/v1/ramadan",
            params={"latitude": 999, "longitude": 31.2357}
        )
        assert response.status_code == 422

    def test_ramadan_calendar_all_days_have_times(self):
        response = client.get(
            "/api/v1/ramadan/calendar",
            params={"latitude": 30.0444, "longitude": 31.2357, "year": 1446}
        )
        data = response.json()
        for day in data["calendar"]:
            assert day["suhoor"] != ""
            assert day["iftar"] != ""
