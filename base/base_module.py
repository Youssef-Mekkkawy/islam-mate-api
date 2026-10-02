from fastapi import Request
from kernel.service_container import ServiceContainer


class BaseModule:
    name: str = ""
    version: str = "1.0.0"
    dependencies: list = []

    def __init__(self, service_container: ServiceContainer):
        self.db = service_container.db
        self.cache = service_container.cache
        self.logger = service_container.logger
        self.config = service_container.config
        self.translator = service_container.translator

    def translate(self, data: dict, lang: str = "en") -> dict:
        return self.translator.translate(data, lang)

    def get_lang(self, request: Request, lang: str = "en") -> str:
        path = request.url.path
        if "/ar/" in path or path.endswith("/ar"):
            return "ar"
        if "/en/" in path or path.endswith("/en"):
            return "en"
        return lang

    def register_routes(self, router):
        raise NotImplementedError(
            f"Module '{self.name}' must implement register_routes()"
        )
