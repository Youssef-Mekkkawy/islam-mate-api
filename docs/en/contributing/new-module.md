# Adding a New Module

## File Structure

```
modules/
└── my_module/
    ├── __init__.py
    └── module.py
```

## Module Template

```python
from fastapi import APIRouter, Query, Request
from base.base_module import BaseModule


class Module(BaseModule):
    name = "my_module"
    version = "1.0.0"
    dependencies = []

    def register_routes(self, router: APIRouter):
        router.add_api_route(
            "/my-endpoint",
            self.my_handler,
            methods=["GET"]
        )

    async def my_handler(
        self,
        request: Request,
        lang: str = Query("en", description="Language: en or ar")
    ):
        lang = self.get_lang(request, lang)
        return {
            "message": self.translate(
                {"ar": "مرحبا", "en": "Hello"},
                lang
            )
        }
```

## Enable in config.yaml

```yaml
modules:
  my_module: true
```

## Write Tests

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestMyModule:

    def test_my_endpoint(self):
        response = client.get("/api/v1/my-endpoint")
        assert response.status_code == 200

    def test_my_endpoint_arabic(self):
        response = client.get("/api/v1/ar/my-endpoint")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "مرحبا"
```

## Run Tests

```bash
pytest tests/test_my_module.py -v
```

## Module Rules

- Always inherit from `BaseModule`
- Always implement `register_routes()`
- Always support `lang` query param
- Always use `self.get_lang()` to detect language
- Always write tests for every endpoint
- Use `self.translate()` for all text responses
