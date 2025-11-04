from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from src.core.logging import get_logger, log_exception
from src.domain.exceptions import RedaktoException
from typing import Any, Dict, List, Union

logger = get_logger(__name__)

async def redakto_exception_handler(request: Request, ex: RedaktoException) -> JSONResponse:
    """
    Handle custom Redakto exceptions.
    
    :param request: The incoming request
    :param ex: The Redakto exception
    :return: JSON response with error details
    """
    logger.error(
        f"path: {request.url.path} | "
        f"method: {request.method} | "
        f"redakto_exception: {ex.message} | "
        f"details: {ex.details}"
    )
    
    return JSONResponse(
        status_code=ex.status_code,
        content={
            "path": request.url.path,
            "method": request.method,
            "error": ex.__class__.__name__,
            "message": ex.message,
            "details": ex.details
        }
    )

def _format_validation_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format Pydantic validation errors to be JSON-serializable.
    Removes non-serializable objects like ValueError instances.
    
    :param errors: Raw validation errors from Pydantic
    :return: JSON-serializable error list
    """
    formatted_errors = list()
    for error in errors:
        formatted_error = {
            "type": error.get("type"),
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "input": error.get("input")
        }
        
        if "ctx" in error and error["ctx"]:
            ctx = error["ctx"]
            formatted_ctx = dict()
            for key, value in ctx.items():
                if isinstance(value, Exception):
                    formatted_ctx[key] = str(value)
                else:
                    formatted_ctx[key] = value
            formatted_error["ctx"] = formatted_ctx
        
        formatted_errors.append(formatted_error)
    
    return formatted_errors

async def validation_exception_handler(request: Request, ex: Union[RequestValidationError, PydanticValidationError]) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    :param request: The incoming request
    :param ex: The validation exception
    :return: JSON response with validation errors
    """
    errors = ex.errors() if hasattr(ex, 'errors') else [{"msg": str(ex)}]
    formatted_errors = _format_validation_errors(errors)
    
    logger.error(
        f"path: {request.url.path} | "
        f"method: {request.method} | "
        f"validation_exception: invalid_request | "
        f"details: {formatted_errors}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "path": request.url.path,
            "method": request.method,
            "error": ex.__class__.__name__,
            "message": "invalid_request",
            "details": formatted_errors
        }
    )

async def generic_exception_handler(request: Request, ex: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions.
    
    :param request: The incoming request
    :param ex: The exception
    :return: JSON response with error details
    """
    log_exception(
        f"Unhandled exception on {request.method} {request.url.path}",
        exception_type=ex.__class__.__name__
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "path": request.url.path,
            "method": request.method,
            "error": "internal_server_error",
            "message": "An unexpected error occurred."
        }
    )