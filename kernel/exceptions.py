"""
Custom exception classes for Islam Mate API.
All modules raise these instead of raw HTTPException.
"""

from typing import Optional


class IslamicAPIException(Exception):
    """Base exception for all Islam Mate API errors."""

    def __init__(
        self,
        code: str,
        message: str,
        message_ar: str = "",
        status_code: int = 400,
        details: Optional[dict] = None,
    ):
        self.code = code
        self.message = message
        self.message_ar = message_ar
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundException(IslamicAPIException):
    def __init__(self, resource: str = "Resource", resource_ar: str = "المورد"):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} not found.",
            message_ar=f"{resource_ar} غير موجود.",
            status_code=404,
        )


class ValidationException(IslamicAPIException):
    def __init__(self, message: str, message_ar: str = "خطأ في البيانات المدخلة.", details: Optional[dict] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            message_ar=message_ar,
            status_code=422,
            details=details,
        )


class UnauthorizedException(IslamicAPIException):
    def __init__(self):
        super().__init__(
            code="UNAUTHORIZED",
            message="Invalid or missing API key.",
            message_ar="مفتاح API غير صالح أو مفقود.",
            status_code=401,
        )


class RateLimitException(IslamicAPIException):
    def __init__(self, retry_after: int = 60):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Please slow down.",
            message_ar="طلبات كثيرة جداً. يرجى التباطؤ.",
            status_code=429,
            details={"retry_after": retry_after},
        )


class ModuleDisabledException(IslamicAPIException):
    def __init__(self, module: str):
        super().__init__(
            code="MODULE_DISABLED",
            message=f"The '{module}' module is currently disabled.",
            message_ar=f"وحدة '{module}' معطلة حالياً.",
            status_code=503,
        )


class ConfigException(IslamicAPIException):
    def __init__(self, message: str):
        super().__init__(
            code="CONFIG_ERROR",
            message=message,
            message_ar="خطأ في الإعدادات.",
            status_code=500,
        )