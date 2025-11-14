from typing import Any, Dict, List, Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from core.exceptions import (
    ConfigurationException,
    PredictionException,
    ResourceNotFoundException
)
from core.logging import get_logger, log_exception


logger = get_logger(__name__)

async def resource_not_found_exception_handler(request: Request, 
                                               ex: ResourceNotFoundException) -> JSONResponse:
    """
    Handle ResourceNotFoundException.
    
    :param request: The incoming request
    :param ex: The ResourceNotFoundException
    :return: JSON response with error details
    """
    logger.error(
        f"path: {request.url.path} | "
        f"method: {request.method} | "
        f"message: {ex.message} | "
        f"details: {ex.details}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "path": request.url.path,
            "method": request.method,
            "error": ex.__class__.__name__,
            "message": ex.message,
            "details": ex.details
        }
    )

async def configuration_exception_handler(request: Request, 
                                          ex: ConfigurationException) -> JSONResponse:
    """
    Handle ConfigurationException.
    
    :param request: The incoming request
    :param ex: The ConfigurationException
    :return: JSON response with error details
    """
    logger.error(
        f"path: {request.url.path} | "
        f"method: {request.method} | "
        f"message: {ex.message} | "
        f"details: {ex.details}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "path": request.url.path,
            "method": request.method,
            "error": ex.__class__.__name__,
            "message": ex.message,
            "details": ex.details
        }
    )

async def prediction_exception_handler(request: Request, 
                                       ex: PredictionException) -> JSONResponse:
    """
    Handle PredictionException.
    
    :param request: The incoming request
    :param ex: The PredictionException
    :return: JSON response with error details
    """
    logger.error(
        f"path: {request.url.path} | "
        f"method: {request.method} | "
        f"message: {ex.message} | "
        f"details: {ex.details}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

async def validation_exception_handler(request: Request, 
                                       ex: Union[
                                           RequestValidationError, 
                                           PydanticValidationError]) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    :param request: The incoming request
    :param ex: The validation exception
    :return: JSON response with validation errors
    """
    errors = ex.errors() if hasattr(ex, 'errors') else [{"msg": str(ex)}]
    formatted_errors = _format_validation_errors(errors)
    details = {"validation_errors": formatted_errors}
    
    logger.error(
        f"path: {request.url.path} | "
        f"method: {request.method} | "
        f"message: Request validation failed | "
        f"details: {details}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "path": request.url.path,
            "method": request.method,
            "error": ex.__class__.__name__,
            "message": "Request validation failed",
            "details": details
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
        f"path: {request.url.path} | "
        f"method: {request.method} | "
        f"message: {str(ex)}"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "path": request.url.path,
            "method": request.method,
            "error": ex.__class__.__name__,
            "message": "An unexpected error occurred."
        }
    )