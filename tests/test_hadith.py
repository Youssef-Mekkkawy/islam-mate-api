import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHadith:

    def test_get_collections(self):
        response = client.get("/api/v1/hadith")
        assert response.status_code == 200
        data = response.json()
        assert "total_collections" in data
        assert "collections" in data
        assert data["total_collections"] >= 7

    def test_get_collections_arabic(self):
        response = client.get("/api/v1/ar/hadith")
        assert response.status_code == 200

    def test_get_collections_english(self):
        response = client.get("/api/v1/en/hadith")
        assert response.status_code == 200

    def test_collection_structure(self):
        response = client.get("/api/v1/hadith")
        data = response.json()
        col = data["collections"][0]
        assert "id" in col
        assert "name" in col
        assert "total" in col

    def test_get_bukhari(self):
        response = client.get("/api/v1/hadith/bukhari")
        assert response.status_code == 200
        data = response.json()
        assert data["collection"] == "bukhari"
        assert data["total"] > 0
        assert "hadiths" in data

    def test_get_bukhari_pagination(self):
        response = client.get("/api/v1/hadith/bukhari?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["hadiths"]) == 10
        assert data["page"] == 1

    def test_get_bukhari_hadith_1(self):
        response = client.get("/api/v1/hadith/bukhari/1")
        assert response.status_code == 200
        data = response.json()
        assert data["hadith"]["number"] == 1
        assert "text" in data["hadith"]

    def test_get_bukhari_arabic(self):
        response = client.get("/api/v1/ar/hadith/bukhari/1")
        assert response.status_code == 200
        data = response.json()
        assert "text" in data["hadith"]

    def test_get_nawawi40(self):
        response = client.get("/api/v1/hadith/nawawi40")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 40

    def test_get_nawawi40_hadith_1(self):
        response = client.get("/api/v1/hadith/nawawi40/1")
        assert response.status_code == 200
        data = response.json()
        assert data["hadith"]["number"] == 1

    def test_get_invalid_collection(self):
        response = client.get("/api/v1/hadith/invalid_xyz")
        assert response.status_code == 404

    def test_get_invalid_hadith_number(self):
        response = client.get("/api/v1/hadith/bukhari/999999")
        assert response.status_code == 404

    def test_get_random(self):
        response = client.get("/api/v1/hadith/random")
        assert response.status_code == 200
        data = response.json()
        assert "collection" in data
        assert "hadith" in data

    def test_get_random_arabic(self):
        response = client.get("/api/v1/ar/hadith/random")
        assert response.status_code == 200

    def test_get_random_from_collection(self):
        response = client.get("/api/v1/hadith/random?collection=bukhari")
        assert response.status_code == 200
        data = response.json()
        assert data["collection"] == "bukhari"

    def test_hadith_structure(self):
        response = client.get("/api/v1/hadith/bukhari/1")
        data = response.json()
        hadith = data["hadith"]
        assert "number" in hadith
        assert "text" in hadith
        assert "grade" in hadith
        assert "reference" in hadith
