# -*- coding: utf-8 -*-
from typing import Any, Optional, Dict
import yaml
import io
import os
import logging


class YamlLoader:
    # Static class variables to store configurations
    _reconstruction_config: Optional[dict] = None
    _reconstruction_config_path: str = "config/conf.yml"

    DEFAULT_CONFIG = {
        "plot_conf": {"height": 400, "width": 550, "x": 230, "y": 80},
        "reconstruction_conf": {
            "detect_soft_faults": False,
            "excitation_type": "Step",
            "file_name": "",
            "level": 1,
            "max_complexity": 6,
            "min_complexity": 2,
            "parent_folder": "",
            "path_length": 15,
            "peak_height": 0.01,
            "processed_parameters": {},
            "tests_number": 50,
        },
        "signal_processing_conf": {
            "filter": "Bandpass",
            "filter_band": {1, 99},
            "gating": "0:0",
            "peak_distance": 0.068,
            "prominence": 0.003,
            "show_distance_plot": True,
            "show_frequency_plot": True,
            "apply_derivative": False,
            "apply_integral": False,
            "speed": 190000000.0,
            "window": "boxcar",
        },
    }

    @classmethod
    def _get_default_config(cls) -> dict:
        """Return default configuration structure"""
        return cls.DEFAULT_CONFIG.copy()

    @classmethod
    def _create_config_file_with_defaults(cls, path: str) -> None:
        """Create configuration file with default values"""
        try:
            # Ensure the directory exists
            config_dir = os.path.dirname(path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)

            # Create the file with defaults
            default_config = cls._get_default_config()
            cls._write_yml(path, default_config)
            logging.info(f"Created configuration file with defaults: {path}")

        except Exception as e:
            logging.error(f"Failed to create default configuration file: {e}")
            raise

    @classmethod
    def _write_yml(cls, path: str, data: Any) -> None:
        """Write data to YAML file"""
        with io.open(path, "w", encoding="utf8") as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)

    @classmethod
    def _read_yml(cls, path: str) -> Any:
        """Read YAML file and return data"""
        try:
            with open(path, "r") as stream:
                data_loaded = yaml.safe_load(stream)
                return data_loaded if data_loaded is not None else {}
        except FileNotFoundError:
            logging.warning(f"Configuration file not found: {path}")
            logging.info("Creating configuration file with default values...")
            cls._create_config_file_with_defaults(path)
            # Try reading again after creating the file
            with open(path, "r") as stream:
                data_loaded = yaml.safe_load(stream)
                return data_loaded if data_loaded is not None else {}
        except Exception as e:
            logging.error(f"Error reading configuration file {path}: {e}")
            logging.info("Using default configuration values")
            return cls._get_default_config()

    @classmethod
    def load_reconstruction_config(cls) -> dict:
        """Load reconstruction configuration"""
        if cls._reconstruction_config is None:
            cls._reconstruction_config = cls._read_yml(cls._reconstruction_config_path)
        return cls._reconstruction_config or {}

    @classmethod
    def get_reconstruction_config(cls) -> dict:
        """Get current reconstruction configuration"""
        if cls._reconstruction_config is None:
            cls.load_reconstruction_config()
        return cls._reconstruction_config or {}

    @classmethod
    def update_reconstruction_config(cls, config: dict) -> None:
        """Update reconstruction configuration in memory"""
        cls._reconstruction_config = config

    @classmethod
    def save_reconstruction_config(cls) -> None:
        """Save reconstruction configuration to file"""
        if cls._reconstruction_config is not None:
            cls._write_yml(cls._reconstruction_config_path, cls._reconstruction_config)

    @classmethod
    def save_all_configs(cls) -> None:
        """Save all configurations to their respective files"""
        cls.save_reconstruction_config()

    @classmethod
    def get_safe(cls, config: Dict[str, Any], path: str, default: Any = None) -> Any:
        """
        Safely get a value from nested configuration using dot notation.

        Args:
            config: Configuration dictionary
            path: Dot-separated path (e.g., "reconstruction_conf.file_name")
            default: Default value if path doesn't exist

        Returns:
            The value at the path or the default value
        """
        try:
            keys = path.split(".")
            value = config

            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    # Try to get default from DEFAULT_CONFIG
                    if default is None:
                        default = cls._get_default_value(path)

                    if default is not None:
                        logging.info(
                            f"Using default value for missing config key '{path}': {default}"
                        )
                        return default
                    else:
                        raise KeyError(
                            f"Configuration key '{path}' not found and no default provided"
                        )

            return value

        except Exception as e:
            if default is not None:
                logging.warning(
                    f"Error accessing config path '{path}': {e}. Using default: {default}"
                )
                return default
            else:
                default_value = cls._get_default_value(path)
                if default_value is not None:
                    logging.warning(
                        f"Error accessing config path '{path}': {e}. Using default: {default_value}"
                    )
                    return default_value
                else:
                    raise

    @classmethod
    def _get_default_value(cls, path: str) -> Any:
        """Get default value from DEFAULT_CONFIG for the given path."""
        try:
            keys = path.split(".")
            value = cls.DEFAULT_CONFIG

            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None

            return value

        except Exception:
            return None

    @classmethod
    def ensure_section_exists(cls, config: Dict[str, Any], section: str) -> None:
        """
        Ensure that a configuration section exists, creating it with defaults if needed.

        Args:
            config: Configuration dictionary to modify
            section: Section name (e.g., "reconstruction_conf")
        """
        if section not in config:
            if section in cls.DEFAULT_CONFIG:
                config[section] = cls.DEFAULT_CONFIG[section].copy()
                logging.info(
                    f"Created missing config section '{section}' with default values"
                )
            else:
                config[section] = {}
                logging.warning(
                    f"Created empty config section '{section}' (no defaults available)"
                )

    @classmethod
    def ensure_key_exists(
        cls, config: Dict[str, Any], path: str, default: Any = None
    ) -> None:
        """
        Ensure that a configuration key exists, setting it to default if needed.

        Args:
            config: Configuration dictionary to modify
            path: Dot-separated path (e.g., "reconstruction_conf.file_name")
            default: Default value to set if key doesn't exist
        """
        try:
            keys = path.split(".")
            current = config

            # Navigate to parent and ensure all intermediate dicts exist
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            # Set the final key if it doesn't exist
            final_key = keys[-1]
            if final_key not in current:
                if default is None:
                    default = cls._get_default_value(path)

                if default is not None:
                    current[final_key] = default
                    logging.info(
                        f"Set missing config key '{path}' to default: {default}"
                    )

        except Exception as e:
            logging.error(f"Error ensuring config key '{path}' exists: {e}")

    @classmethod
    def validate_and_fix_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration and add missing keys with default values.

        Args:
            config: Configuration dictionary to validate and fix

        Returns:
            Fixed configuration dictionary
        """
        # Ensure main sections exist
        for section in cls.DEFAULT_CONFIG:
            cls.ensure_section_exists(config, section)

        # Ensure all default keys exist
        for section, section_config in cls.DEFAULT_CONFIG.items():
            if isinstance(section_config, dict):
                for key, default_value in section_config.items():
                    cls.ensure_key_exists(config, f"{section}.{key}", default_value)

        return config
