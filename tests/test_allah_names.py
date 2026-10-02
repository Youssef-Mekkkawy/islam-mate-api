import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestAllahNames:

    def test_get_all_names(self):
        response = client.get("/api/v1/allah-names")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 99
        assert len(data["names"]) == 99

    def test_get_all_names_arabic(self):
        response = client.get("/api/v1/ar/allah-names")
        assert response.status_code == 200
        data = response.json()
        assert len(data["names"]) == 99

    def test_get_all_names_english(self):
        response = client.get("/api/v1/en/allah-names")
        assert response.status_code == 200

    def test_name_structure(self):
        response = client.get("/api/v1/allah-names")
        data = response.json()
        name = data["names"][0]
        assert "number" in name
        assert "arabic" in name
        assert "transliteration" in name
        assert "name" in name
        assert "meaning" in name

    def test_get_by_number(self):
        response = client.get("/api/v1/allah-names/1")
        assert response.status_code == 200
        data = response.json()
        assert data["number"] == 1
        assert data["arabic"] == "الله"

    def test_get_by_number_arabic(self):
        response = client.get("/api/v1/ar/allah-names/1")
        assert response.status_code == 200

    def test_get_ar_rahman(self):
        response = client.get("/api/v1/allah-names/2")
        assert response.status_code == 200
        data = response.json()
        assert data["arabic"] == "الرحمن"
        assert data["transliteration"] == "Ar-Rahman"

    def test_get_last_name(self):
        response = client.get("/api/v1/allah-names/99")
        assert response.status_code == 200
        data = response.json()
        assert data["number"] == 99

    def test_invalid_number_zero(self):
        response = client.get("/api/v1/allah-names/0")
        assert response.status_code == 404

    def test_invalid_number_100(self):
        response = client.get("/api/v1/allah-names/100")
        assert response.status_code == 404

    def test_get_random(self):
        response = client.get("/api/v1/allah-names/random")
        assert response.status_code == 200
        data = response.json()
        assert "number" in data
        assert 1 <= data["number"] <= 99

    def test_get_random_arabic(self):
        response = client.get("/api/v1/ar/allah-names/random")
        assert response.status_code == 200

    def test_lang_query_param(self):
        response = client.get("/api/v1/allah-names/1?lang=ar")
        assert response.status_code == 200
