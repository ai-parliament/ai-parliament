import os
import yaml
from typing import List, Dict, Any, Union

from logger import Logger

logger = Logger(name="ConfigManager")
class ConfigManager:
    def __init__(self, config_path: Union[str, List[str]]):
        if isinstance(config_path, str):
            self.config_paths = [config_path]
        else:
            self.config_paths = config_path
        
        self.config = self._load_default_config()
        
        for path in self.config_paths:
            self.config.update(self._load_config_file(os.getcwd() + "/" + path))
    
    def _load_default_config(self):
        default_config = {
            "env_path": "config/.env",
            "api_key_env_var": "OPENAI_API_KEY",
            "app": {
                "title": "app",
                "layout": "wide"
            },
            "default_model": "gpt-4o-mini",
            "available_models": ["gpt-4o-mini", "gpt-3.5-turbo"],
        }
        logger.info("Default configuration loaded")
        return default_config
    
    def _load_config_file(self, file_path: str) -> Dict:
        logger.info(f"Loading configuration file {file_path}")
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    logger.info(f"Configuration file {file_path} found.")
                    return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading configuration file {file_path}: {e}")

        logger.warning(f"No configuration found at {file_path}.")
        return {}     
    
    def get_config(self) -> Dict[str, Any]:
        logger.info(f"Returning current configuration: {self.config}")
        return self.config
    
    def get_value(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            logger.info(f"Found value for key '{key}' : {value}")
            return value
        except (KeyError, TypeError):
            logger.info(f"Value not found for key '{key}'. Returning default value: {default}")
            return default
    
    def save_config(self, config_path: str) -> bool:
        logger.info(f"Saving configuration to {config_path}")
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            logger.info("Directory created successfully.")
            
            with open(config_path, "w") as file:
                logger.info(f"Writing config to {config_path}")
                yaml.dump(self.config, file, default_flow_style=False)
            
            logger.info(f"Configuration saved to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
        