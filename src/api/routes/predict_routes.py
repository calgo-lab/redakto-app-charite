from fastapi import APIRouter, Depends, Request
from src.api.schemas.detect_entities_schemas import DetectEntitiesRequest, DetectEntitiesResponse
from src.application.services.prediction_service import PredictionService
from src.core.logging import get_logger
from src.domain.exceptions import EntitySetNotFoundError, ModelNotFoundError, PredictionError, UnsupportedOperationForModel

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/predict",
    tags=["Prediction"],
    responses={500: {"description": "Internal server error"}}
)

def get_prediction_service(request: Request) -> PredictionService:
    return request.app.state.prediction_service

@router.post(
    "/detect_entities", 
    response_model=DetectEntitiesResponse,
    summary="Detect named entities in text",
    description="Detects and labels named entities in German text using a specified NER model and entity set.",
    response_description="Returns a list of detected entities including position (start, end), label and entity token for each input text.",
    operation_id="detectEntities",
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
    
    :param request: DetectEntitiesRequest entity_set_id, model_id, fine_grained mode, input_texts
    :param service: PredictionService instance
    :return: DetectEntitiesResponse with detected entities

    Raises:
        EntitySetNotFoundError: If the specified entity set does not exist
        ModelNotFoundError: If the specified model does not exist for the given entity set
        UnsupportedOperationForModel: If the specified model does not support NER operations
        PredictionError: If an error occurs during entity detection
    """
    try:
        return service.detect_entities(request)
    except (EntitySetNotFoundError, ModelNotFoundError, UnsupportedOperationForModel):
        raise
    except Exception as e:
        raise PredictionError(message=str(e))