from src.api.schemas.detect_entities_schemas import DetectEntitiesRequest, DetectEntitiesResponse, EntityItem
from src.core.logging import get_logger
from src.domain.exceptions import UnsupportedOperationForModel
from src.domain.sentence_with_boundary import SentenceWithBoundary
from src.infrastructure.services.model_service import ModelService
from src.utils.coarse_label_utils import CoarseLabelUtils
from typing import Dict, List, Set

import json
import pandas as pd
import re

class PredictionService:
    """
    PredictionService is responsible for handling entity detection requests.
    Works as a bridge between the infrastructure and api layers.
    """
    def __init__(self, model_service: ModelService):
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
            raise UnsupportedOperationForModel(entity_set_id, model_id, model_type, 'NER')

        output: List[List[EntityItem]] = list()
        model_inference_maker = self._model_service.get_model_inference_maker(request.entity_set_id, request.model_id)
        for input_text in request.input_texts:
            model_output: List[SentenceWithBoundary] = model_inference_maker.infer(input_text)
            for swb in model_output:
                self.logger.info(f'{swb.sentence.to_tagged_string()}')
            entities = self._convert_flair_sentences_to_entity_items(input_text, model_output)

            if not request.fine_grained:
                entities = self._convert_to_coarse_labeled_entities(entity_set_id, input_text, entities)

            output.append(entities)
        return DetectEntitiesResponse(output=output)

    def _convert_flair_sentences_to_entity_items(self, 
                                                 input_text: str, 
                                                 model_output: List[SentenceWithBoundary]) -> List[EntityItem]:
        """
        Convert SentenceWithBoundary objects to EntityItem instances.
        :param input_text: The original input text.
        :param model_output: The model output containing SentenceWithBoundary objects.
        :return: A list of EntityItem instances.
        """

        items: List[EntityItem] = list()
        token_id = 0
        for swb in model_output:
            next_cursor = swb.start
            sentence = swb.sentence
            labels = sentence.get_labels()
            for label in labels:
                text = label.data_point.text
                start = input_text.find(text, next_cursor, swb.end)

                if start == -1 and re.search(r'\s', text):
                    
                    tokens = text.split()
                    if len(tokens) >= 2:
                        first_token = tokens[0]
                        last_token = tokens[-1]
                        first_pos = input_text.find(first_token, next_cursor, swb.end)
                        
                        if first_pos != -1:
                            last_pos = input_text.find(last_token, first_pos + len(first_token), swb.end)
                            
                            if last_pos != -1:
                                boundary_start = first_pos
                                boundary_end = last_pos + len(last_token)
                                extracted_text = input_text[boundary_start: boundary_end]
                                
                                normalized_extracted = re.sub(r'\s+', ' ', extracted_text)
                                normalized_predicted = re.sub(r'\s+', ' ', text)
                                
                                if normalized_extracted == normalized_predicted:
                                    start = boundary_start
                                    end = boundary_end
                                    token_id += 1
                                    next_cursor = end
                                    
                                    items.append(
                                        EntityItem(token_id='T'+str(token_id), 
                                                   label=label.value, 
                                                   start=start, 
                                                   end=end, 
                                                   token=input_text[start: end])
                                    )
                elif start != -1:
                    end = start + len(text)
                    token_id += 1
                    next_cursor = end
                    
                    items.append(
                        EntityItem(token_id='T'+str(token_id), 
                                   label=label.value, 
                                   start=start, 
                                   end=end, 
                                   token=input_text[start: end])
                    )
                else:
                    token_id += 1
                    items.append(
                        EntityItem(token_id='T'+str(token_id), 
                                   label=label.value, 
                                   start=-1, 
                                   end=-1, 
                                   token=text)
                    )

        self.logger.info(json.dumps([item.model_dump() for item in items], indent=2, ensure_ascii=False))
        return items

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