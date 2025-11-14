from typing import List

from api.schemas.app_info_schemas import (
    EntitySetDetailsResponse,
    EntitySetLabelResponse,
    FineGrainedLabelResponse,
    SupportedModelDetailsResponse,
    SupportedModelResponse
)
from config_handlers.entity_set_models_config_handler import (
    EntitySetModel, 
    EntitySetModelsConfigHandler, 
    SupportedModel
)
from core.exceptions import EntitySetNotFoundException, ModelNotFoundException


class AppInfoService:
    """
    AppInfoService is responsible for providing application configuration 
    information using the config_handlers/*ConfigHandler classes which loads 
    different configuration *.yml files.
    """

    def __init__(self):
        """
        Initializes the AppInfoService by loading the different configuration files.
        """
        self._entity_set_models_config = EntitySetModelsConfigHandler.load_from_file()

    def get_entity_set_ids(self) -> List[str]:
        """
        Returns a list of all available entity set IDs configured in the application.

        :return: List of entity set identifiers
        """
        return [es.entity_set_id for es in self._entity_set_models_config.entity_sets]

    def get_supported_models_ids_for_entity_set_id(self, entity_set_id: str) -> List[str]:
        """
        Returns a list of supported model IDs for a given entity set ID.
        
        :param entity_set_id: The ID of the entity set
        :return: List of supported model IDs
        """
        entity_set: EntitySetModel = self._entity_set_models_config.get_entity_set(entity_set_id)
        if not entity_set:
            raise EntitySetNotFoundException(entity_set_id)
        
        return [sm.model_id for sm in entity_set.supported_models]

    def get_entity_set_details_by_id(self, entity_set_id: str) -> EntitySetDetailsResponse | None:
        """
        Returns the details of an entity set by its ID.

        :param entity_set_id: The ID of the entity set
        :return: EntitySetModel or None if not found
        """
        entity_set: EntitySetModel = self._entity_set_models_config.get_entity_set(entity_set_id)
        if not entity_set:
            raise EntitySetNotFoundException(entity_set_id)
        
        labels_response = list()
        for label in entity_set.entity_set_labels:
            fine_grained_labels = [
                FineGrainedLabelResponse(
                    id=fg.id,
                    description=fg.description
                )
                for fg in label.fine_grained
            ]
            
            labels_response.append(
                EntitySetLabelResponse(
                    id=label.id,
                    description=label.description,
                    fine_grained=fine_grained_labels
                )
            )
        
        models_response = [
            SupportedModelResponse(
                model_id=sm.model_id,
                model_name=sm.model_name
            )
            for sm in entity_set.supported_models
        ]
        
        return EntitySetDetailsResponse(
            entity_set_id=entity_set.entity_set_id,
            corpus_name=entity_set.corpus_name,
            corpus_doctypes=entity_set.corpus_doctypes,
            corpus_description=entity_set.corpus_description,
            corpus_version=entity_set.corpus_version,
            corpus_languages=entity_set.corpus_languages,
            corpus_links=entity_set.corpus_links,
            entity_set_labels=labels_response,
            supported_models=models_response
        )

    def get_supported_model_details(self, entity_set_id: str, model_id: str) -> SupportedModelDetailsResponse | None:
        """
        Returns the details of a supported model within a specific entity set.

        :param entity_set_id: The ID of the entity set
        :param model_id: The ID of the supported model
        :return: SupportedModelDetailsResponse or None if not found
        """
        entity_set: EntitySetModel = self._entity_set_models_config.get_entity_set(entity_set_id)
        if not entity_set:
            raise EntitySetNotFoundException(entity_set_id)
            
        supported_model: SupportedModel = self._entity_set_models_config.get_supported_model(entity_set_id, model_id)
        if not supported_model:
            raise ModelNotFoundException(entity_set_id, model_id)
        
        if supported_model:
            return SupportedModelDetailsResponse(
                model_id=supported_model.model_id,
                model_name=supported_model.model_name,
                model_description=supported_model.model_description,
                model_links=supported_model.model_links,
                model_type=supported_model.model_type,
                model_type_description=supported_model.model_type_description,
                model_version=supported_model.model_version
            )
        return None