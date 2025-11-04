from flair.models import SequenceTagger
from pathlib import Path
from src.infrastructure.frameworks.cached_model_loader import CachedModelLoader

import flair


class SequenceTaggerLoader(CachedModelLoader):
    """
    Responsible for loading a Flair SequenceTagger model - given a model_path.
    """
    def __init__(self, 
                 model_name_or_path: str, 
                 loading_strategy: str = "local_disk_storage"):
        """
        :param model_name_or_path: The path or name of the Flair model to load.
        :param loading_strategy: The strategy to use for loading the model (e.g., local_disk_storage).
        """
        super().__init__(model_name_or_path, loading_strategy)
        self._cache_root: Path = Path("/app/flair_cache_root")

    def _load_model(self) -> SequenceTagger:
        """
        Load the Flair SequenceTagger model and return the model object.
        :return: The loaded SequenceTagger model object.
        """
        flair.cache_root = self._cache_root
        try:
            if self.loading_strategy == "local_disk_storage":
                return SequenceTagger.load(self.model_name_or_path / "model.pt")
            else:
                raise ValueError(f"Unsupported loading strategy: {self.loading_strategy} for model at {self.model_name_or_path}")
        except Exception as e:
            print(f"Failed to load Flair model for {self._model_name_or_path}: {e}")