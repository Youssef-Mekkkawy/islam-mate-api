import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestQibla:

    def test_get_qibla_success(self):
        response = client.get(
            "/api/v1/qibla",
            params={"latitude": 30.0444, "longitude": 31.2357}
        )
        assert response.status_code == 200
        data = response.json()
        assert "location" in data
        assert "qibla" in data

    def test_qibla_response_structure(self):
        response = client.get(
            "/api/v1/qibla",
            params={"latitude": 30.0444, "longitude": 31.2357}
        )
        data = response.json()
        qibla = data["qibla"]
        assert "bearing" in qibla
        assert "direction" in qibla
        assert "distance_km" in qibla
        assert "kaaba" in qibla

    def test_qibla_bearing_range(self):
        response = client.get(
            "/api/v1/qibla",
            params={"latitude": 30.0444, "longitude": 31.2357}
        )
        data = response.json()
        bearing = data["qibla"]["bearing"]
        assert 0 <= bearing <= 360

    def test_qibla_cairo_direction(self):
        response = client.get(
            "/api/v1/qibla",
            params={"latitude": 30.0444, "longitude": 31.2357}
        )
        data = response.json()
        assert data["qibla"]["direction"] == "SE"
        assert 130 <= data["qibla"]["bearing"] <= 145

    def test_qibla_arabic(self):
        response = client.get(
            "/api/v1/qibla",
            params={"latitude": 30.0444, "longitude": 31.2357, "lang": "ar"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "درجة" in data["qibla"]["description"]

    def test_qibla_invalid_latitude(self):
        response = client.get(
            "/api/v1/qibla",
            params={"latitude": 999, "longitude": 31.2357}
        )
        assert response.status_code == 422

    def test_qibla_invalid_longitude(self):
        response = client.get(
            "/api/v1/qibla",
            params={"latitude": 30.0444, "longitude": 999}
        )
        assert response.status_code == 422

    def test_qibla_kaaba_coordinates(self):
        response = client.get(
            "/api/v1/qibla",
            params={"latitude": 30.0444, "longitude": 31.2357}
        )
        data = response.json()
        kaaba = data["qibla"]["kaaba"]
        assert kaaba["lat"] == 21.4225
        assert kaaba["lng"] == 39.8262

    def test_qibla_distance_cairo(self):
        response = client.get(
            "/api/v1/qibla",
            params={"latitude": 30.0444, "longitude": 31.2357}
        )
        data = response.json()
        distance = data["qibla"]["distance_km"]
        assert 1200 <= distance <= 1400
