"""
Request logging middleware for Islam Mate API.
Logs every request: method, path, IP, status, duration.
Uses loguru. Config-driven via config.yaml logging section.
"""

import time
import sys
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from loguru import logger
from kernel.services.config_reader import ConfigReader


def setup_logger():
    """Configure loguru from config.yaml. Call once at startup."""
    config = ConfigReader()
    config.load()

    log_cfg = config.get("logging", {})
    if not isinstance(log_cfg, dict):
        return

    if not log_cfg.get("enabled", True):
        logger.disable("__main__")
        return

    level = log_cfg.get("level", "INFO").upper()
    log_format = log_cfg.get("format", "text")
    log_file = log_cfg.get("log_file", "logs/api.log")
    rotation = log_cfg.get("rotation", "10 MB")
    retention = log_cfg.get("retention", "7 days")

    # Remove default handler
    logger.remove()

    if log_format == "json":
        fmt = '{"time":"{time:YYYY-MM-DD HH:mm:ss}","level":"{level}","message":"{message}"}'
    else:
        fmt = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | {message}"

    # Console output
    logger.add(sys.stdout, format=fmt, level=level, colorize=(log_format != "json"))

    # File output
    logger.add(
        log_file,
        format=fmt,
        level=level,
        rotation=rotation,
        retention=retention,
        encoding="utf-8",
    )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs every request with method, path, IP, status code, and duration."""

    SKIP_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        status = response.status_code

        # Choose log level based on status + duration
        if status >= 500:
            logger.error(f"{method} {path} | IP: {ip} | {status} | {duration_ms:.1f}ms")
        elif status >= 400:
            logger.warning(f"{method} {path} | IP: {ip} | {status} | {duration_ms:.1f}ms")
        elif duration_ms > 500:
            logger.warning(f"SLOW {method} {path} | IP: {ip} | {status} | {duration_ms:.1f}ms")
        else:
            logger.info(f"{method} {path} | IP: {ip} | {status} | {duration_ms:.1f}ms")

        return response