from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from kernel.kernel import Kernel
from kernel.services.auth import validate_key
from kernel.services.config_reader import ConfigReader

kernel = Kernel()
kernel.discover()

app = FastAPI(
    title="Islam Mate API",
    description="Open-source Islamic REST API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

EXEMPT_EXACT = ["/", "/health", "/docs", "/redoc", "/openapi.json"]
EXEMPT_PREFIX = ["/docs/", "/redoc/", "/api/v1/auth/"]


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    config = ConfigReader()
    config.load()
    mode = config.get("app.mode", "development")
    auth_enabled = config.get("security.auth_enabled", False)

    if mode == "development" or not auth_enabled:
        return await call_next(request)

    path = request.url.path

    if path in EXEMPT_EXACT:
        return await call_next(request)

    if any(path.startswith(p) for p in EXEMPT_PREFIX):
        return await call_next(request)

    api_key = (
        request.headers.get("X-API-Key") or
        request.headers.get("Authorization", "").replace("Bearer ", "") or
        request.query_params.get("api_key")
    )

    if not api_key:
        return JSONResponse(
            status_code=401,
            content={"error": "API key required", "message": "Pass via X-API-Key header or ?api_key= param"}
        )

    if not validate_key(api_key):
        return JSONResponse(
            status_code=403,
            content={"error": "Invalid API key", "message": "Key not found or inactive"}
        )

    return await call_next(request)


kernel.register_routes(app)


@app.on_event("startup")
async def startup():
    await kernel.init_services()


@app.on_event("shutdown")
async def shutdown():
    await kernel.shutdown()


@app.get("/")
async def root():
    return {"name": "Islam Mate API", "version": "1.0.0", "docs": "/docs", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}

