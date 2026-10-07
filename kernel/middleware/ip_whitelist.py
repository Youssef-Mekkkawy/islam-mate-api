"""
IP Whitelist middleware for Islam Mate API.
Disabled by default — zero performance cost when off.
Supports exact IPs and CIDR ranges (e.g. 192.168.1.0/24).
Config-driven via config.yaml ip_whitelist section.
"""

import ipaddress
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import JSONResponse
from kernel.services.config_reader import ConfigReader


class IPWhitelistMiddleware(BaseHTTPMiddleware):

    ALWAYS_ALLOW = {"/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        config = ConfigReader()
        config.load()

        wl_cfg = config.get("ip_whitelist", {})
        if not isinstance(wl_cfg, dict) or not wl_cfg.get("enabled", False):
            return await call_next(request)

        # Skip docs + health
        if request.url.path in self.ALWAYS_ALLOW:
            return await call_next(request)

        client_ip = request.client.host if request.client else None
        allowed_list = wl_cfg.get("allowed_ips", [])

        if client_ip and self._is_allowed(client_ip, allowed_list):
            return await call_next(request)

        message = wl_cfg.get("block_message", "Access denied.")
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": {
                    "code": "FORBIDDEN",
                    "message": message,
                    "message_ar": "الوصول مرفوض.",
                    "details": None,
                },
                "status": 403,
            },
        )

    @staticmethod
    def _is_allowed(client_ip: str, allowed_list: list) -> bool:
        try:
            client = ipaddress.ip_address(client_ip)
        except ValueError:
            return False

        for entry in allowed_list:
            try:
                # Try as network (CIDR)
                if "/" in str(entry):
                    if client in ipaddress.ip_network(entry, strict=False):
                        return True
                # Try as exact IP
                elif client == ipaddress.ip_address(entry):
                    return True
            except ValueError:
                continue

        return False