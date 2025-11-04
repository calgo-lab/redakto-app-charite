from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class EntitySetQueryParams(BaseModel):
    """
    Query parameter for entity set ID.
    """
    entity_set_id: str = Field(
        ...,
        description="The entity set identifier (e.g., 'codealltag', 'grascco')",
        min_length=1
    )

    @field_validator('entity_set_id')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """
        Validate that string fields are not empty or do not contain only whitespace.

        :param v: The field value
        :return: The validated value
        :raises ValueError: If validation fails
        """
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or contain only whitespace')
        return v.strip()

class ModelQueryParams(BaseModel):
    """
    Query parameters for model operations.
    """
    entity_set_id: str = Field(
        ...,
        description="The entity set identifier (e.g., 'codealltag', 'grascco')",
        min_length=1
    )
    model_id: str = Field(
        ...,
        description="The model identifier (e.g., 'xlm-roberta-large', 'codealltag-xml-roberta-large')",
        min_length=1
    )
    
    @field_validator('entity_set_id', 'model_id')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """
        Validate that string fields are not empty or do not contain only whitespace.

        :param v: The field value
        :return: The validated value
        :raises ValueError: If validation fails
        """
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or contain only whitespace')
        return v.strip()

class FineGrainedLabelResponse(BaseModel):
    """
    Response model for fine-grained labels.
    """
    id: str = Field(..., description="ID of the fine-grained label")
    description: str = Field(..., description="Description of the fine-grained label")

class EntitySetLabelResponse(BaseModel):
    """
    Response model for entity set labels.
    """
    id: str = Field(..., description="ID of the coarse-grained label")
    description: str = Field(..., description="Description of the coarse-grained label")
    fine_grained: List[FineGrainedLabelResponse] = Field(default_factory=list, description="List of fine-grained labels")

class SupportedModelResponse(BaseModel):
    """
    Response model for supported models.
    """
    model_id: str = Field(..., description="Unique identifier for the model")
    model_name: str = Field(..., description="Display name of the model")

class SupportedModelDetailsResponse(BaseModel):
    """
    Response model for supported model details.
    """
    model_id: str = Field(..., description="Unique identifier for the model")
    model_name: str = Field(..., description="Display name of the model")
    model_description: str = Field(..., description="Description of the model")
    model_type: Optional[str] = Field(None, description="Type of the model (e.g., 'NER', 'NER-PG')")
    model_type_description: Optional[str] = Field(None, description="Description of the model type")
    model_links: List[str] = Field(default_factory=list, description="List of links related to the model")
    model_version: Optional[str] = Field(None, description="Version of the model")

class EntitySetDetailsResponse(BaseModel):
    """
    Response model for entity set details.
    """
    entity_set_id: str = Field(..., description="Unique identifier for the entity set")
    corpus_name: Optional[str] = Field(None, description="Name of the corpus")
    corpus_doctype: Optional[str] = Field(None, description="Document type of the corpus")
    corpus_description: Optional[str] = Field(None, description="Description of the corpus")
    corpus_version: Optional[str] = Field(None, description="Version of the corpus")
    corpus_links: List[str] = Field(default_factory=list, description="List of links related to the corpus")
    entity_set_labels: List[EntitySetLabelResponse] = Field(default_factory=list, description="List of entity labels")
    supported_models: List[SupportedModelResponse] = Field(default_factory=list, description="List of supported models")