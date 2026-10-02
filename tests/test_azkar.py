import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def get_first_valid_category_id():
    response = client.get("/api/v1/azkar")
    categories = response.json()["categories"]
    for cat in categories:
        if cat["count"] > 0:
            return cat["id"]
    return None


class TestAzkar:

    def test_get_categories(self):
        response = client.get("/api/v1/azkar")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "categories" in data
        assert data["total"] > 0

    def test_get_categories_english(self):
        response = client.get("/api/v1/en/azkar")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0

    def test_get_categories_arabic(self):
        response = client.get("/api/v1/ar/azkar")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0

    def test_category_structure(self):
        response = client.get("/api/v1/azkar")
        data = response.json()
        cat = data["categories"][0]
        assert "id" in cat
        assert "slug" in cat
        assert "title" in cat
        assert "count" in cat

    def test_get_azkar_by_id(self):
        cat_id = get_first_valid_category_id()
        assert cat_id is not None
        response = client.get(f"/api/v1/azkar/{cat_id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "azkar" in data
        assert len(data["azkar"]) > 0

    def test_get_azkar_by_id_arabic(self):
        cat_id = get_first_valid_category_id()
        response = client.get(f"/api/v1/ar/azkar/{cat_id}")
        assert response.status_code == 200
        data = response.json()
        assert "azkar" in data

    def test_get_azkar_by_id_english(self):
        cat_id = get_first_valid_category_id()
        response = client.get(f"/api/v1/en/azkar/{cat_id}")
        assert response.status_code == 200
        data = response.json()
        assert "azkar" in data

    def test_get_azkar_not_found(self):
        response = client.get("/api/v1/azkar/99999")
        assert response.status_code == 404

    def test_get_azkar_by_slug(self):
        response = client.get("/api/v1/azkar/slug/morning_evening")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "morning_evening"

    def test_get_azkar_by_invalid_slug(self):
        response = client.get("/api/v1/azkar/slug/invalid_slug_xyz")
        assert response.status_code == 404

    def test_azkar_item_structure(self):
        cat_id = get_first_valid_category_id()
        response = client.get(f"/api/v1/azkar/{cat_id}")
        data = response.json()
        item = data["azkar"][0]
        assert "id" in item
        assert "text" in item
        assert "repeat" in item
        assert "source" in item

    def test_get_random_azkar(self):
        response = client.get("/api/v1/azkar/random/item")
        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert "azkar" in data

    def test_get_random_azkar_arabic(self):
        response = client.get("/api/v1/ar/azkar/random/item")
        assert response.status_code == 200

    def test_lang_query_param(self):
        cat_id = get_first_valid_category_id()
        response = client.get(f"/api/v1/azkar/{cat_id}?lang=ar")
        assert response.status_code == 200
