import logging
import re
from typing import Any, List
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, status_code: int = 400, detail: str = "An error occurred"):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class NotFoundException(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(status.HTTP_404_NOT_FOUND, f"{resource} not found")


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status.HTTP_409_CONFLICT, detail)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "You do not have permission to perform this action"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail)


class BadRequestException(AppException):
    def __init__(self, detail: str = "Invalid request"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)


class ValidationException(AppException):
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail)


def _clean_validation_message(msg: str) -> str:
    """Strip pydantic technical prefixes like 'Value error, ' for cleaner messages."""
    if msg.startswith("Value error, "):
        return msg[len("Value error, "):]
    return msg


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "detail": exc.detail,
                "data": None,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        detail_msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": detail_msg,
                "detail": detail_msg,
                "data": None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        formatted_errors: List[dict[str, Any]] = []
        messages: List[str] = []

        for err in exc.errors():
            loc = err.get("loc", [])
            # Filter out 'body', 'query', 'path' if present to get field name
            field = ".".join(str(p) for p in loc if p not in ("body", "query", "path", "header"))
            if not field and loc:
                field = str(loc[-1])

            clean_msg = _clean_validation_message(err.get("msg", "Invalid input"))
            formatted_errors.append({
                "field": field or "payload",
                "message": clean_msg,
                "type": err.get("type", "validation_error"),
            })
            if field:
                messages.append(f"'{field}': {clean_msg}")
            else:
                messages.append(clean_msg)

        summary_message = "; ".join(messages) if messages else "Validation failed for request parameters"

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": f"Validation error: {summary_message}",
                "detail": f"Validation error: {summary_message}",
                "errors": formatted_errors,
                "data": None,
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.error(f"Integrity Error on {request.url.path}: {exc}")
        err_str = str(exc.orig or exc).lower()

        if "unique" in err_str or "duplicate key" in err_str:
            detail_msg = "A record with this identifier, name, or phone number already exists."
        elif "foreign key" in err_str:
            detail_msg = "Referenced record does not exist or has dependent records preventing this action."
        elif "check constraint" in err_str:
            detail_msg = "The submitted data violates database constraints."
        else:
            detail_msg = "Database integrity constraint violation. Please verify all referenced data."

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success": False,
                "message": detail_msg,
                "detail": detail_msg,
                "data": None,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled Server Error on {request.method} {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "An unexpected server error occurred. Please try again later.",
                "detail": "Internal server error",
                "data": None,
            },
        )
