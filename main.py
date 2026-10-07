from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from kernel.kernel import Kernel
from kernel.services.auth import validate_key
from kernel.services.config_reader import ConfigReader
from kernel.rate_limiter import limiter, rate_limit_exceeded_handler, is_rate_limited
from modules.location.platforms import router as location_platforms_router
from kernel.middleware.logging_middleware import LoggingMiddleware, setup_logger
from kernel.middleware.ip_whitelist import IPWhitelistMiddleware

kernel = Kernel()
kernel.discover()

# --- Load config for startup settings ---
_config = ConfigReader()
_config.load()

# --- CORS — config-driven ---
_cors_cfg = _config.get("cors", {})
_cors_enabled = _cors_cfg.get("enabled", True) if isinstance(_cors_cfg, dict) else True
_cors_origins = _cors_cfg.get("allowed_origins", ["*"]) if isinstance(_cors_cfg, dict) else ["*"]
_cors_methods = _cors_cfg.get("allowed_methods", ["*"]) if isinstance(_cors_cfg, dict) else ["*"]
_cors_headers = _cors_cfg.get("allowed_headers", ["*"]) if isinstance(_cors_cfg, dict) else ["*"]

app = FastAPI(
    title="Islam Mate API",
    description="Open-source Islamic REST API",
    version="1.0.0"
)

setup_logger()
app.add_middleware(LoggingMiddleware)
app.add_middleware(IPWhitelistMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

if _cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_credentials=False,
        allow_methods=_cors_methods,
        allow_headers=_cors_headers,
    )

EXEMPT_EXACT = ["/", "/health", "/docs", "/redoc", "/openapi.json"]
EXEMPT_PREFIX = ["/docs/", "/redoc/", "/api/v1/auth/"]


def _err(status: int, code: str, message: str, message_ar: str = "", details=None):
    """Unified error envelope — matches kernel/error_handler.py format."""
    return JSONResponse(
        status_code=status,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "message_ar": message_ar,
                "details": details,
            },
            "status": status,
        },
    )


@app.middleware("http")
async def main_middleware(request: Request, call_next):
    config = ConfigReader()
    config.load()
    mode = config.get("app.mode", "development")
    auth_enabled = config.get("security.auth_enabled", False)
    rate_limiting = config.get("security.rate_limiting", False)

    path = request.url.path
    is_exempt = path in EXEMPT_EXACT or any(path.startswith(p) for p in EXEMPT_PREFIX)

    # Rate limiting check
    if rate_limiting and not is_exempt:
        ip = request.client.host
        if is_rate_limited(ip):
            return _err(
                429,
                "RATE_LIMIT_EXCEEDED",
                "Too many requests. Please slow down.",
                "طلبات كثيرة جداً. يرجى التباطؤ.",
                {"retry_after": 60},
            )

    # Auth check
    if mode == "development" or not auth_enabled or is_exempt:
        return await call_next(request)

    api_key = (
        request.headers.get("X-API-Key")
        or request.headers.get("Authorization", "").replace("Bearer ", "")
        or request.query_params.get("api_key")
    )

    if not api_key:
        return _err(
            401,
            "UNAUTHORIZED",
            "Invalid or missing API key.",
            "مفتاح API غير صالح أو مفقود.",
        )

    if not validate_key(api_key):
        return _err(
            403,
            "FORBIDDEN",
            "API key not found or inactive.",
            "مفتاح API غير موجود أو غير مفعل.",
        )

    return await call_next(request)


kernel.register_routes(app)
app.include_router(location_platforms_router)


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