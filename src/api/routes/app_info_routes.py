from typing import List

from fastapi import APIRouter, Depends, Request

from api.schemas.app_info_schemas import (
    EntitySetDetailsResponse,
    EntitySetQueryParams,
    ModelQueryParams,
    SupportedModelDetailsResponse
)
from application.services.app_info_service import AppInfoService


router = APIRouter(
    prefix="/api/app_info",
    tags=["App Information"],
    responses={
        500: {"description": "Internal server error"}
    }
)

def get_app_info_service(request: Request) -> AppInfoService:
    """
    Dependency to retrieve the AppInfoService instance from the application state.

    :param request: FastAPI Request object
    :return: AppInfoService instance
    """
    return request.app.state.app_info_service

@router.get(
    "/get_entity_set_ids",
    response_model=List[str],
    summary="Get all entity set IDs",
    description="Returns a list of all available entity set IDs configured in the application.",
    response_description="List of entity set identifiers",
    operation_id="GetEntitySetIds",
    responses={
        200: {"description": "Successfully retrieved entity set IDs"},
        500: {"description": "Internal server error during entity set IDs retrieval"}
    }
)
def get_entity_set_ids(service: AppInfoService = Depends(get_app_info_service)) -> List[str]:
    """
    Retrieve all available entity set IDs.

    :param service: AppInfoService instance
    :return: List of entity set IDs
    """
    return service.get_entity_set_ids()
    
@router.get(
    "/get_supported_model_ids",
    response_model=List[str],
    summary="Get supported model IDs for an entity set",
    description="Returns a list of all supported model IDs for the specified entity set ID.",
    response_description="List of model identifiers for the given entity set ID",
    operation_id="GetSupportedModelIds",
    responses={
        200: {"description": "Successfully retrieved supported model IDs"},
        404: {"description": "Entity set not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error during supported model IDs retrieval"}
    }
)
def get_supported_model_ids(query: EntitySetQueryParams = Depends(),
                            service: AppInfoService = Depends(get_app_info_service)) -> List[str]:
    """
    Retrieve all supported model IDs for a specific entity set.

    :param query: Query parameter containing the entity set ID, such as "codealltag" or "grascco"
    :param service: AppInfoService instance
    :return: List of supported model IDs for the specified entity set
    """
    return service.get_supported_models_ids_for_entity_set_id(query.entity_set_id)

@router.get(
    "/get_entity_set_details",
    response_model=EntitySetDetailsResponse,
    summary="Get details of an entity set by ID",
    description="Returns the details of an entity set given its ID.",
    response_description="Entity set details",
    operation_id="GetEntitySetDetails",
    responses={
        200: {"description": "Successfully retrieved entity set details"},
        404: {"description": "Entity set not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error during entity set details retrieval"}
    }
)
def get_entity_set_details(query: EntitySetQueryParams = Depends(),
                           service: AppInfoService = Depends(get_app_info_service)) -> EntitySetDetailsResponse:
    """
    Retrieve the details of an entity set by its ID.

    :param query: Query parameter containing the entity set ID, such as "codealltag" or "grascco"
    :param service: AppInfoService instance
    :return: Details of the specified entity set
    """
    return service.get_entity_set_details_by_id(query.entity_set_id)

@router.get(
    "/get_supported_model_details",
    response_model=SupportedModelDetailsResponse,
    summary="Get details of a supported model",
    description="Returns the details of a supported model within a specific entity set.",
    response_description="Supported model details",
    operation_id="GetSupportedModelDetails",
    responses={
        200: {"description": "Successfully retrieved supported model details"},
        404: {"description": "Entity set or model not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error during supported model details retrieval"}
    }
)
def get_supported_model_details(queries: ModelQueryParams = Depends(),
                                service: AppInfoService = Depends(get_app_info_service)) -> SupportedModelDetailsResponse:
    """
    Retrieve the details of a supported model by its ID within a specific entity set.

    :param queries: Query parameters containing the entity set ID and model ID
    :param service: AppInfoService instance
    :return: Details of the specified supported model
    """
    return service.get_supported_model_details(queries.entity_set_id, queries.model_id)