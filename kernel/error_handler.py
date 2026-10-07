"""
Global error handler for Islam Mate API.
Registers handlers on the FastAPI app for all error types.
Unified JSON envelope:
  { "success": false, "error": { "code", "message", "message_ar", "details" }, "status": 4xx }
"""

import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from kernel.exceptions import IslamicAPIException


def _error_response(
    status_code: int,
    code: str,
    message: str,
    message_ar: str = "",
    details=None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "message_ar": message_ar,
                "details": details,
            },
            "status": status_code,
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    """Call this once in kernel startup to register all handlers."""

    # 1. Our custom exceptions
    @app.exception_handler(IslamicAPIException)
    async def islamic_api_exception_handler(request: Request, exc: IslamicAPIException):
        return _error_response(
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            message_ar=exc.message_ar,
            details=exc.details,
        )

    # 2. Pydantic / FastAPI validation errors (422)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Flatten Pydantic's verbose error list into something readable
        field_errors = {}
        for error in exc.errors():
            field = " → ".join(str(loc) for loc in error["loc"] if loc != "query")
            field_errors[field] = error["msg"]

        return _error_response(
            status_code=422,
            code="VALIDATION_ERROR",
            message="Request validation failed. Check the 'details' field.",
            message_ar="فشل التحقق من الطلب. راجع حقل 'details'.",
            details=field_errors,
        )

    # 3. Standard HTTP errors (404, 405, etc.)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        messages = {
            400: ("Bad request.", "طلب غير صالح."),
            401: ("Unauthorized.", "غير مصرح."),
            403: ("Access denied.", "الوصول مرفوض."),
            404: ("The requested resource was not found.", "المورد المطلوب غير موجود."),
            405: ("Method not allowed.", "الطريقة غير مسموحة."),
            429: ("Too many requests.", "طلبات كثيرة جداً."),
            500: ("Internal server error.", "خطأ داخلي في الخادم."),
            503: ("Service temporarily unavailable.", "الخدمة غير متاحة مؤقتاً."),
        }
        msg_en, msg_ar = messages.get(exc.status_code, (str(exc.detail), ""))
        codes = {
            400: "BAD_REQUEST", 401: "UNAUTHORIZED", 403: "FORBIDDEN",
            404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED", 429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_ERROR", 503: "SERVICE_UNAVAILABLE",
        }
        code = codes.get(exc.status_code, "HTTP_ERROR")

        return _error_response(
            status_code=exc.status_code,
            code=code,
            message=msg_en,
            message_ar=msg_ar,
        )

    # 4. Catch-all for unhandled exceptions (500)
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Log the full traceback (will integrate with logging middleware later)
        traceback.print_exc()
        return _error_response(
            status_code=500,
            code="INTERNAL_ERROR",
            message="An unexpected error occurred.",
            message_ar="حدث خطأ غير متوقع.",
        )