from fastapi import APIRouter, Depends, Request

from api.schemas.detect_entities_schemas import DetectEntitiesRequest, DetectEntitiesResponse
from application.services.prediction_service import PredictionService


router = APIRouter(
    prefix="/api/predict",
    tags=["Prediction"],
    responses={
        500: {"description": "Internal server error"}
    }
)

def get_prediction_service(request: Request) -> PredictionService:
    """
    Dependency to retrieve the PredictionService instance from the application state.

    :param request: FastAPI Request object
    :return: PredictionService instance
    """
    return request.app.state.prediction_service

@router.post(
    "/detect_entities",
    response_model=DetectEntitiesResponse,
    summary="Detect named entities in text",
    description="Detects and labels named entities in German text using a specified NER model and entity set.",
    response_description="Returns a list of detected entities including position (start, end), label and entity token for each input text",
    operation_id="DetectEntities",
    responses={
        200: {"description": "Successfully processed input texts for named entity detection"},
        404: {"description": "Entity set or model not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error during entity detection"}
    }
)
def detect_entities(request: DetectEntitiesRequest,
                    service: PredictionService = Depends(get_prediction_service)) -> DetectEntitiesResponse:
    """
    Detect named entities in the provided texts using the specified model and entity set.
    
    :param request: DetectEntitiesRequest with entity_set_id, model_id, fine_grained mode, input_texts
    :param service: PredictionService instance
    :return: DetectEntitiesResponse with detected entities
    """
    return service.detect_entities(request)