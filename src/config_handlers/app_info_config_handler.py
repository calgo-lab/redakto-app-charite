from __future__ import annotations
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ValidationError

import yaml


class AppInfoConfig(BaseModel):
    """
    Configuration model for application information.
    """
    app_name: str
    app_version: str
    app_short_description: str
    app_log_level: str
    backend_url: str
    entity_set_info: str
    label_type_info: str
    supported_models_info: str


class AppInfoConfigHandler:
    """
    Loads and provides access to the application information configuration.
    """

    DEFAULT_CONFIG_PATH = (
        Path(__file__).resolve().parent.parent.parent / "configs" / "app_info_config.yml"
    )

    def __init__(self, raw: dict, config: AppInfoConfig):
        """
        Initializes the AppInfoConfigHandler with raw and validated configuration.
        
        :param raw: Raw configuration dictionary.
        :param config: Validated AppInfoConfig instance.
        """
        self._raw = raw
        self._config = config

    @classmethod
    def load_from_file(cls, path: Optional[Path] = None) -> "AppInfoConfigHandler":
        """
        Load the application information configuration from a YAML file.
        
        :param path: Optional path to the configuration file. If not provided, DEFAULT_CONFIG_PATH is used.
        :return: An instance of AppInfoConfigHandler with the loaded configuration.
        :raises FileNotFoundError: If the configuration file does not exist.
        :raises ValidationError: If the YAML structure is invalid.
        """
        cfg_path = Path(path) if path else cls.DEFAULT_CONFIG_PATH
        if not cfg_path.exists():
            raise FileNotFoundError(f"Config file not found: {cfg_path}")

        raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or dict()
        
        try:
            config = AppInfoConfig(**raw)
        except ValidationError as ve:
            raise ValidationError(ve.errors()) from ve

        return cls(raw=raw, config=config)

    @classmethod
    def load_from_yaml_string(cls, yaml_str: str) -> "AppInfoConfigHandler":
        """
        Load the application information configuration from a YAML string.
        
        :param yaml_str: YAML string containing the configuration.
        :return: An instance of AppInfoConfigHandler with the loaded configuration.
        :raises ValidationError: If the YAML structure is invalid.
        """
        raw = yaml.safe_load(yaml_str) or dict()
        
        try:
            config = AppInfoConfig(**raw)
        except ValidationError as ve:
            raise ValidationError(ve.errors()) from ve
        
        return cls(raw=raw, config=config)

    def get_config(self) -> AppInfoConfig:
        """
        Get the validated configuration object.
        
        :return: AppInfoConfig instance.
        """
        return self._config

    @property
    def app_name(self) -> str:
        """
        Get the application name.

        :return: Application name.
        """
        return self._config.app_name

    @property
    def app_version(self) -> str:
        """
        Get the application version.

        :return: Application version.
        """
        return self._config.app_version

    @property
    def app_short_description(self) -> str:
        """
        Get the application short description.

        :return: Application short description.
        """
        return self._config.app_short_description

    @property
    def app_log_level(self) -> str:
        """
        Get the application log level.

        :return: Application log level.
        """
        return self._config.app_log_level

    @property
    def backend_url(self) -> str:
        """
        Get the backend URL.

        :return: Backend URL.
        """
        return self._config.backend_url

    @property
    def entity_set_info(self) -> str:
        """
        Get the entity set information description.

        :return: Entity set information description.
        """
        return self._config.entity_set_info

    @property
    def label_type_info(self) -> str:
        """
        Get the label type information description.

        :return: Label type information description.
        """
        return self._config.label_type_info

    @property
    def supported_models_info(self) -> str:
        """
        Get the supported models information description.

        :return: Supported models information description.
        """
        return self._config.supported_models_info

    def as_dict(self) -> dict:
        """
        Return the raw configuration as a dictionary.
        
        :return: Dictionary representation of the configuration.
        """
        return self._raw.copy()