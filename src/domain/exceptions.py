from typing import Any, Dict, Optional

class RedaktoException(Exception):
    """
    Base exception for Redakto errors
    """

    def __init__(self, message: str, status_code: int, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or dict()
        super().__init__(self.message)

class ResourceNotFoundError(RedaktoException):
    """
    Raised when a requested resource is not found
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)

class ConfigurationError(RedaktoException):
    """
    Raised when configuration is invalid or missing
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)



class EntitySetNotFoundError(ResourceNotFoundError):
    """
    Raised when an entity set is not found in the registry
    """
    def __init__(self, entity_set_id: str):
        super().__init__(
            f"Entity set '{entity_set_id}' not found"
        )

class ModelNotFoundError(ResourceNotFoundError):
    """
    Raised when a model is not found in the registry for the given entity set id and model id
    """
    def __init__(self, entity_set_id: str, model_id: str):
        super().__init__(
            f"Model '{model_id}' not found for entity set '{entity_set_id}'"
        )

class UnsupportedModelLoadingStrategyError(ConfigurationError):
    """
    Raised when an unsupported model loading strategy is encountered
    """
    def __init__(self, entity_set_id: str, model_id: str, strategy: str):
        super().__init__(
            f"Unsupported model loading strategy '{strategy}' for model '{model_id}' in entity set '{entity_set_id}'"
        )

class UnsupportedModelImplTypeError(ConfigurationError):
    """
    Raised when an unsupported model impl type is encountered
    """
    def __init__(self, entity_set_id: str, model_id: str, model_impl: str):
        super().__init__(
            f"Unsupported model impl type: '{model_impl}' for model '{model_id}' in entity set '{entity_set_id}'"
        )

class ModelLoadError(RedaktoException):
    """
    Raised when a model fails to load
    """
    def __init__(self, entity_set_id: str, model_id: str, details: Optional[Dict[str, Any]] = None):
        msg: str = f"Failed to load model '{model_id}' for entity set '{entity_set_id}'"
        super().__init__(msg, status_code=500, details=details)

class UnsupportedOperationForModel(ConfigurationError):
    """
    Raised when model_type is mismatched for respective operation
    """
    def __init__(self, entity_set_id: str, model_id: str, model_type: str, required_model_type: str):
        super().__init__(
            f"Unsupported operation requested, required model_type '{required_model_type}', but found model_type '{model_type}' for model '{model_id}' in entity set '{entity_set_id}'"
        )

class PredictionError(RedaktoException):
    """
    Raised when prediction fails.
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)

