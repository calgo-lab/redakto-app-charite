from typing import List

from pydantic import BaseModel, Field, field_validator


class DetectEntitiesRequest(BaseModel):
    """
    Request schema for detecting entities in texts.
    """

    entity_set_id: str = Field(
        ...,
        description="The entity set identifier (e.g., 'codealltag', 'grascco')",
        min_length=1
    )
    model_id: str = Field(
        ...,
        description="The model identifier (e.g., 'xlm-roberta-large', 'codealltag-xml-roberta-large') to use for entity detection",
        min_length=1
    )
    fine_grained: bool = Field(
        ...,
        description="Whether to use fine-grained entity labels"
    )
    input_texts: List[str] = Field(
        ...,
        description="List of input texts to analyze for entity detection",
        min_items=1
    )

    @field_validator("input_texts")
    @classmethod
    def validate_input_texts(cls, v: List[str]) -> List[str]:
        """
        Validate that input_texts does not contain empty strings.
        """
        empty_indices = [i for i, text in enumerate(v) if not text.strip()]
        if empty_indices:
            raise ValueError(
                f'input_texts cannot contain empty strings or whitespace-only strings at indices: {empty_indices}'
            )
        return v
    
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

class EntityItem(BaseModel):
    """
    Response model for a detected entity item.
    """
    
    token_id: str = Field(..., alias='Token_ID')
    label: str = Field(..., alias='Label')
    start: int = Field(..., alias='Start')
    end: int = Field(..., alias='End')
    token: str = Field(..., alias='Token')

    class Config:
        populate_by_name = True
        validate_by_name = True

class DetectEntitiesResponse(BaseModel):
    """
    Response model for detected entities in texts.
    """
    
    output: List[List[EntityItem]]