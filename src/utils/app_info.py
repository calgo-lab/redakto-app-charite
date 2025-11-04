from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

import yaml

class SupportedModel(BaseModel):
    model_id: str
    model_name: str
    model_description: str = ""
    model_links: List[str] = Field(default_factory=list)
    model_type: str
    model_type_description: str
    model_loading_strategy: str
    model_directory_name: List[str]
    model_version: str
    model_impl: str
    model_system_requirements: List[str]
    model_tokenizer_params: Dict[str, Any] = Field(default_factory=dict)
    model_generate_params: Dict[str, Any] = Field(default_factory=dict)

class FineGrainedLabel(BaseModel):
    id: str
    description: str
    background_color: Optional[str] = None
    border_color: Optional[str] = None

class EntitySetLabel(BaseModel):
    id: str
    description: str
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    fine_grained: List[FineGrainedLabel]

class EntitySetModel(BaseModel):
    entity_set_id: str
    corpus_name: str
    corpus_doctype: str
    corpus_description: str
    corpus_version: str
    corpus_language: str
    corpus_links: List[str]
    supported_models_root_dir: List[str]
    supported_models: List[SupportedModel]
    entity_set_labels: List[EntitySetLabel]
    sample_texts: List[str]

class AppInfoData(BaseModel):
    app_name: str
    app_version: str
    backend_url: str
    entity_set_info: str
    label_type_info: str
    supported_models_info: str
    entity_set_models: List[EntitySetModel]

class AppInfo:
    """
    Utility for loading and accessing app information and configuration.
    """

    DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config/app_info.yml"

    def __init__(self, config: AppInfoData):
        self._config = config

    @classmethod
    def load(cls, config_path: Optional[str | Path] = None) -> AppInfo:
        """
        Load configuration from a file.
        If no path is given, loads from DEFAULT_CONFIG_PATH.
        """
        path = Path(config_path) if config_path else cls.DEFAULT_CONFIG_PATH
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # Parse entity sets and their models with full validation
        entity_sets = []
        for es_data in data["entity_set_models"]:
            models = [SupportedModel.model_validate(model) for model in es_data["supported_models"]]
            labels = [EntitySetLabel.model_validate(label_data) for label_data in es_data.get("entity_set_labels", [])]
            texts = es_data.get("sample_texts", [])
            entity_sets.append(EntitySetModel(
                entity_set_id=es_data["entity_set_id"],
                corpus_name=es_data["corpus_name"],
                corpus_doctype=es_data["corpus_doctype"],
                corpus_description=es_data["corpus_description"],
                corpus_version=es_data["corpus_version"],
                corpus_language=es_data["corpus_language"],
                corpus_links=es_data["corpus_links"],
                supported_models_root_dir=es_data["supported_models_root_dir"],
                supported_models=models,
                entity_set_labels=labels,
                sample_texts=texts
            ))
        
        app_info_data = AppInfoData(
            app_name=data["app_name"],
            app_version=data["app_version"],
            backend_url=data["backend_url"],
            entity_set_info=data["entity_set_info"],
            label_type_info=data["label_type_info"],
            supported_models_info=data["supported_models_info"],
            entity_set_models=entity_sets
        )
        return cls(app_info_data)

    @property
    def app_name(self) -> str:
        return self._config.app_name

    @property
    def app_version(self) -> str:
        return self._config.app_version

    @property
    def backend_url(self) -> str:
        return self._config.backend_url

    @property
    def entity_set_info(self) -> str:
        return self._config.entity_set_info

    @property
    def label_type_info(self) -> str:
        return self._config.label_type_info

    @property
    def supported_models_info(self) -> str:
        return self._config.supported_models_info

    @property
    def entity_sets(self) -> List[EntitySetModel]:
        return self._config.entity_set_models

    def get_entity_set(self, entity_set_id: str) -> EntitySetModel | None:
        """
        Find an entity set by its ID.
        """
        return next((es for es in self._config.entity_set_models if es.entity_set_id == entity_set_id), None)

    def get_supported_model(self, entity_set_id: str, model_id: str) -> SupportedModel | None:
        """
        Find a supported model by its ID within a specific entity set.
        """
        entity_set = self.get_entity_set(entity_set_id)
        if entity_set:
            return next((m for m in entity_set.supported_models if m.model_id == model_id), None)
        return None