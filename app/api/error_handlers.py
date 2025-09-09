from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.core.logging import logger

async def handle_value_error(request: Request, exc: ValueError):
    """Handler for ValueErrors, which can indicate not found or bad input."""
    logger.log_event("validation.error", {"error": str(exc)})
    # Check for "not found" messages to return a 404
    if "not found" in str(exc).lower():
        status_code = 404
        error_type = "NotFound"
    else:
        status_code = 400
        error_type = "InvalidInput"

    return JSONResponse(
        status_code=status_code,
        content={"error": error_type, "message": str(exc)},
    )

async def handle_permission_error(request: Request, exc: PermissionError):
    """Handler for PermissionErrors."""
    logger.log_event("permission.denied", {"error": str(exc)})
    return JSONResponse(
        status_code=403,
        content={"error": "PermissionDenied", "message": str(exc)},
    )

async def handle_app_exception(request: Request, exc: AppException):
    """Handler for custom application exceptions."""
    logger.log_event("app.exception", {"error": exc.error_code, "detail": exc.message})
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "message": exc.message},
    )

async def handle_http_exception(request: Request, exc: HTTPException):
    """Handler for FastAPI's HTTPException."""
    logger.log_event("http.exception", {"status_code": exc.status_code, "detail": exc.detail})
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HttpException", "message": exc.detail},
    )

async def handle_starlette_http_exception(request: Request, exc: StarletteHTTPException):
    """Handler for Starlette's HTTPException."""
    logger.log_event("http.exception", {"status_code": exc.status_code, "detail": exc.detail})
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HttpException", "message": exc.detail},
    )

async def handle_validation_exception(request: Request, exc: RequestValidationError):
    """Handler for Pydantic's RequestValidationError."""
    logger.log_event("validation.error", {"errors": exc.errors()})

    # Custom formatting can be done here if desired, but default is often good.
    # For this task, we'll create a simplified error message.
    error_messages = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "Validation error")
        error_messages.append(f"Field '{field}': {message}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "UnprocessableEntity",
            "message": "Invalid input provided.",
            "details": error_messages,
        },
    )

async def handle_generic_exception(request: Request, exc: Exception):
    """Handler for generic, unhandled exceptions."""
    logger.log_event("unhandled.exception", {"error": str(exc)})
    # In a real production environment, you would log the full traceback here.
    # import traceback
    # logger.log_event("unhandled.exception.trace", {"trace": traceback.format_exc()})

    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected internal error occurred.",
        },
    )

def register_exception_handlers(app):
    """Register all exception handlers for the FastAPI app."""
    app.add_exception_handler(ValueError, handle_value_error)
    app.add_exception_handler(PermissionError, handle_permission_error)
    app.add_exception_handler(AppException, handle_app_exception)
    app.add_exception_handler(HTTPException, handle_http_exception)
    app.add_exception_handler(StarletteHTTPException, handle_starlette_http_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(Exception, handle_generic_exception)
