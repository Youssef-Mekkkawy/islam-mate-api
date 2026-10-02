from fastapi import Request
from fastapi.routing import APIRouter
from kernel.service_container import ServiceContainer
from kernel.rate_limiter import limiter


class BaseModule:
    name: str = ""
    version: str = "1.0.0"
    dependencies: list = []

    default_limit = "60/minute"
    strict_limit = "30/minute"
    heavy_limit = "10/minute"

    def __init__(self, service_container: ServiceContainer):
        self.db = service_container.db
        self.cache = service_container.cache
        self.logger = service_container.logger
        self.config = service_container.config
        self.translator = service_container.translator

    def translate(self, data: dict, lang: str = "en"):
        return self.translator.translate(data, lang)

    def get_lang(self, request: Request, lang: str = "en") -> str:
        path = request.url.path
        if "/ar/" in path or path.endswith("/ar"):
            return "ar"
        if "/en/" in path or path.endswith("/en"):
            return "en"
        return lang

    def register_routes(self, router: APIRouter):
        raise NotImplementedError(
            f"Module '{self.name}' must implement register_routes()"
        )
