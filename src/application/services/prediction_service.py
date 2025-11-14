from typing import Any, Dict, List, Set

from api.schemas.detect_entities_schemas import DetectEntitiesRequest, DetectEntitiesResponse, EntityItem
from core.exceptions import UnsupportedOperationForModelException
from core.logging import get_logger
from infrastructure.services.model_service import ModelService
from utils.coarse_label_utils import CoarseLabelUtils

import pandas as pd


class PredictionService:
    """
    PredictionService is responsible for handling entity detection requests.
    Works as a bridge between the infrastructure and api layers.
    """

    def __init__(self, model_service: ModelService):
        """
        Initializes the PredictionService with the provided ModelService.
        
        :param model_service: An instance of ModelService to handle model operations.
        """
        self.logger = get_logger(__name__)
        self._model_service = model_service

    def detect_entities(self, request: DetectEntitiesRequest) -> DetectEntitiesResponse:
        """
        Detect entities in the provided texts using the specified model.

        :param request: The request object containing input texts and model information.
        :return: A response object containing the detected entities for the provided texts.
        """
        entity_set_id = request.entity_set_id
        model_id = request.model_id
        model_type = self._model_service.get_model_config(entity_set_id, model_id)['model_type']
        if model_type != 'NER':
            raise UnsupportedOperationForModelException(entity_set_id, model_id, model_type, 'NER')

        model_inference_maker = self._model_service.get_model_inference_maker(request.entity_set_id, request.model_id)
        
        output: List[List[EntityItem]] = list()
        for input_text in request.input_texts:
            entity_items: List[Dict[str, Any]] = model_inference_maker.infer(input_text)
            entities: List[EntityItem] = list()
            for item in entity_items:
                entities.append(EntityItem(**item))
            if not request.fine_grained:
                entities = self._convert_to_coarse_labeled_entities(entity_set_id, input_text, entities)
            output.append(entities)
        return DetectEntitiesResponse(output=output)

    def _convert_to_coarse_labeled_entities(self, 
                                            entity_set_id: str, 
                                            input_text: str, 
                                            fine_grained_entities: List[EntityItem]) -> List[EntityItem]:
        """
        Transform fine-grained entities into coarse-grained entities depending on the 
        mapping related to the entity set.
        
        :param entity_set_id: The ID of the entity set.
        :param input_text: The original input text.
        :param fine_grained_entities: The list of fine-grained entities to transform.
        :return: A list of coarse-grained entities.
        """
        if not fine_grained_entities:
            return list()
        
        annotation_df = pd.DataFrame([
            entity.model_dump(by_alias=True) for entity in fine_grained_entities
        ])

        fine_to_coarse_mapping: Dict[str, str] = dict()
        skip_labels: Set[str] = set()
        if entity_set_id == 'codealltag':
            fine_to_coarse_mapping = {
                "FAMILY": "NAME",
                "FEMALE": "NAME",
                "MALE": "NAME",
                "CITY": "LOCATION",
                "STREET": "LOCATION",
                "STREETNO": "LOCATION",
                "ZIP": "LOCATION",
                "EMAIL": "CONTACT",
                "PHONE": "CONTACT",
                "URL": "CONTACT",
                "UFID": "ID",
                "USER": "ID",
                "ORG": "ORGANIZATION"
            }
        elif entity_set_id == 'grascco':
            fine_to_coarse_mapping = {        
                "NAME_DOCTOR": "NAME",
                "NAME_EXT": "NAME",
                "NAME_OTHER": "NAME",
                "NAME_PATIENT": "NAME",
                "NAME_RELATIVE": "NAME",
                "LOCATION_CITY": "LOCATION",
                "LOCATION_COUNTRY": "LOCATION",
                "LOCATION_OTHER": "LOCATION",
                "LOCATION_STATE": "LOCATION",
                "LOCATION_STREET": "LOCATION",
                "LOCATION_ZIP": "LOCATION",
                "CONTACT_EMAIL": "CONTACT",
                "CONTACT_FAX": "CONTACT",
                "CONTACT_PHONE": "CONTACT",
                "CONTACT_URL": "CONTACT",
                "NAME_USERNAME": "ID",
                "LOCATION_HOSPITAL": "ORGANIZATION",
                "LOCATION_ORGANIZATION": "ORGANIZATION"
            }
            skip_labels = {"NAME_TITLE"}

        merged_entities_df = CoarseLabelUtils.map_to_coarse_labels(annotation_df=annotation_df,
                                                                   input_text=input_text,
                                                                   fine_to_coarse_mapping=fine_to_coarse_mapping,
                                                                   skip_labels=skip_labels,
                                                                   merge_consecutive=True)[0]

        return [EntityItem(**row) for _, row in merged_entities_df.iterrows()]