from fastapi import FastAPI
from fastapi.routing import APIRouter


class Router:
    def register(self, app: FastAPI, modules: list):
        print("Registering module routes...")
        for module in modules:
            router = APIRouter(prefix="/api/v1")
            module.register_routes(router)
            app.include_router(router)
            print(f"Routes registered: {module.name}")
        print("All routes registered.")
