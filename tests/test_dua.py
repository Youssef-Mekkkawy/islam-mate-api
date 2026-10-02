import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestDua:

    def test_get_categories(self):
        response = client.get("/api/v1/dua")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "categories" in data
        assert data["total"] > 0

    def test_get_categories_arabic(self):
        response = client.get("/api/v1/ar/dua")
        assert response.status_code == 200

    def test_get_categories_english(self):
        response = client.get("/api/v1/en/dua")
        assert response.status_code == 200

    def test_category_structure(self):
        response = client.get("/api/v1/dua")
        data = response.json()
        cat = data["categories"][0]
        assert "category" in cat
        assert "count" in cat

    def test_get_dua_by_category(self):
        response = client.get("/api/v1/dua/food")
        assert response.status_code == 200
        data = response.json()
        assert "duas" in data
        assert len(data["duas"]) > 0

    def test_get_dua_arabic(self):
        response = client.get("/api/v1/ar/dua/food")
        assert response.status_code == 200
        data = response.json()
        assert "duas" in data

    def test_get_dua_english(self):
        response = client.get("/api/v1/en/dua/food")
        assert response.status_code == 200
        data = response.json()
        assert "duas" in data

    def test_get_dua_not_found(self):
        response = client.get("/api/v1/dua/invalid_category_xyz")
        assert response.status_code == 404

    def test_dua_item_structure(self):
        response = client.get("/api/v1/dua/food")
        data = response.json()
        item = data["duas"][0]
        assert "id" in item
        assert "text" in item
        assert "repeat" in item
        assert "source" in item

    def test_get_random_dua(self):
        response = client.get("/api/v1/dua/random")
        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert "dua" in data

    def test_get_random_dua_arabic(self):
        response = client.get("/api/v1/ar/dua/random")
        assert response.status_code == 200

    def test_lang_query_param(self):
        response = client.get("/api/v1/dua/food?lang=ar")
        assert response.status_code == 200
