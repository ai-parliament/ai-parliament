"""
Configuration Manager for AI Parliament Frontend

This module handles all configuration settings, text content, UI settings,
and default values for the AI Parliament application using YAML files.
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path


class ConfigManager:
    """Main configuration manager for the AI Parliament application"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self._app_config = None
        self._texts = None
        self._default_parties = None
        
        # Load configurations
        self._load_configurations()
        
        # Backend API configuration
        self.backend_api_url = os.environ.get(
            self._app_config.get("backend", {}).get("api_url_env", "BACKEND_API_URL"),
            self._app_config.get("backend", {}).get("default_api_url", "http://localhost:8000/api")
        )
        
        # Environment-specific settings
        self.is_docker = os.environ.get(
            self._app_config.get("environment", {}).get("docker_env", "DOCKER_ENV"), 
            str(self._app_config.get("environment", {}).get("default_docker", False))
        ).lower() == "true"
        
        self.debug_mode = os.environ.get(
            self._app_config.get("environment", {}).get("debug_env", "DEBUG"), 
            str(self._app_config.get("environment", {}).get("default_debug", False))
        ).lower() == "true"
    
    def _load_configurations(self):
        """Load all configuration files"""
        try:
            # Load main app configuration
            with open(self.config_dir / "app_config.yml", 'r', encoding='utf-8') as f:
                self._app_config = yaml.safe_load(f)
            
            # Load text configuration
            with open(self.config_dir / "texts.yml", 'r', encoding='utf-8') as f:
                self._texts = yaml.safe_load(f)
            
            # Load default parties configuration
            with open(self.config_dir / "default_parties.yml", 'r', encoding='utf-8') as f:
                self._default_parties = yaml.safe_load(f)
                
        except FileNotFoundError as e:
            print(f"Configuration file not found: {e}")
            self._load_fallback_config()
        except yaml.YAMLError as e:
            print(f"Error parsing YAML configuration: {e}")
            self._load_fallback_config()
    
    def _load_fallback_config(self):
        """Load fallback configuration if YAML files are not available"""
        self._app_config = {
            "llm": {
                "default_model": "gpt-4",
                "available_models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                "temperature": {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.1},
                "max_tokens": {"default": 2000, "min": 500, "max": 4000, "step": 100}
            },
            "parliament": {
                "parties": {"default_count": 2, "min_count": 1, "max_count": 10},
                "mps": {"default_per_party": 2, "min_per_party": 1, "max_per_party": 5}
            },
            "ui": {
                "page": {"title": "AI Parliament", "icon": "🏛️", "layout": "wide", "sidebar_state": "expanded"},
                "colors": {
                    "system_message": {"background": "#f0f2f6", "border": "#4e8cff"},
                    "party_message": {"background": "#e6f3ff", "border": "#0068c9"},
                    "politician_message": {"background": "#f5f5f5", "border": "#ff9500"}
                }
            }
        }
        
        self._texts = {
            "titles": {"app_title": "AI Parliament"},
            "buttons": {"start_simulation": "Start Simulation", "reset": "Reset"},
            "messages": {"success": {"simulation_created": "Simulation created successfully!"}}
        }
        
        self._default_parties = {
            "parties": {
                "Prawo i Sprawiedliwosc": {
                    "abbreviation": "PiS",
                    "politicians": [
                        {"name": "Jaroslaw Kaczynski", "role": "Chairman"},
                        {"name": "Antoni Macierewicz", "role": "Member"}
                    ]
                }
            }
        }
    
    def reload_config(self):
        """Reload configuration from files"""
        self._load_configurations()
    
    # LLM Configuration Properties
    @property
    def llm_default_model(self) -> str:
        return self._app_config.get("llm", {}).get("default_model", "gpt-4")
    
    @property
    def llm_available_models(self) -> List[str]:
        return self._app_config.get("llm", {}).get("available_models", ["gpt-4"])
    
    @property
    def llm_temperature_default(self) -> float:
        return self._app_config.get("llm", {}).get("temperature", {}).get("default", 0.7)
    
    @property
    def llm_temperature_range(self) -> tuple:
        temp_config = self._app_config.get("llm", {}).get("temperature", {})
        return (temp_config.get("min", 0.0), temp_config.get("max", 1.0))
    
    @property
    def llm_temperature_step(self) -> float:
        return self._app_config.get("llm", {}).get("temperature", {}).get("step", 0.1)
    
    @property
    def llm_max_tokens_default(self) -> int:
        return self._app_config.get("llm", {}).get("max_tokens", {}).get("default", 2000)
    
    @property
    def llm_max_tokens_range(self) -> tuple:
        tokens_config = self._app_config.get("llm", {}).get("max_tokens", {})
        return (tokens_config.get("min", 500), tokens_config.get("max", 4000))
    
    @property
    def llm_max_tokens_step(self) -> int:
        return self._app_config.get("llm", {}).get("max_tokens", {}).get("step", 100)
    
    # Parliament Configuration Properties
    @property
    def parliament_default_parties(self) -> int:
        return self._app_config.get("parliament", {}).get("parties", {}).get("default_count", 2)
    
    @property
    def parliament_parties_range(self) -> tuple:
        parties_config = self._app_config.get("parliament", {}).get("parties", {})
        return (parties_config.get("min_count", 1), parties_config.get("max_count", 10))
    
    @property
    def parliament_default_mps(self) -> int:
        return self._app_config.get("parliament", {}).get("mps", {}).get("default_per_party", 2)
    
    @property
    def parliament_mps_range(self) -> tuple:
        mps_config = self._app_config.get("parliament", {}).get("mps", {})
        return (mps_config.get("min_per_party", 1), mps_config.get("max_per_party", 5))
    
    # UI Configuration Properties
    @property
    def ui_page_title(self) -> str:
        return self._app_config.get("ui", {}).get("page", {}).get("title", "AI Parliament")
    
    @property
    def ui_page_icon(self) -> str:
        return self._app_config.get("ui", {}).get("page", {}).get("icon", "🏛️")
    
    @property
    def ui_layout(self) -> str:
        return self._app_config.get("ui", {}).get("page", {}).get("layout", "wide")
    
    @property
    def ui_sidebar_state(self) -> str:
        return self._app_config.get("ui", {}).get("page", {}).get("sidebar_state", "expanded")
    
    # Text Management Methods
    def get_text(self, *keys, default: str = "") -> str:
        """Get text by nested keys with optional default"""
        current = self._texts
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return str(current) if current is not None else default
    
    def get_nested_config(self, *keys, default: Any = None) -> Any:
        """Get nested configuration value"""
        current = self._app_config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    
    # Party Management Methods
    def get_default_party_names(self) -> List[str]:
        """Get list of default party names"""
        return list(self._default_parties.get("parties", {}).keys())
    
    def get_default_party_data(self, party_name: str) -> Optional[Dict[str, Any]]:
        """Get default data for a specific party"""
        return self._default_parties.get("parties", {}).get(party_name)
    
    def get_default_politicians(self, party_name: str) -> List[Dict[str, str]]:
        """Get default politicians for a party"""
        party_data = self.get_default_party_data(party_name)
        return party_data.get("politicians", []) if party_data else []
    
    def get_default_abbreviation(self, party_name: str) -> str:
        """Get default abbreviation for a party"""
        party_data = self.get_default_party_data(party_name)
        return party_data.get("abbreviation", "") if party_data else ""
    
    def get_alternative_parties(self, category: str = "international") -> Dict[str, Any]:
        """Get alternative party configurations"""
        return self._default_parties.get("alternative_parties", {}).get(category, {})
    
    # CSS and Styling Methods
    def get_chat_css(self) -> str:
        """Get CSS styles for chat interface"""
        colors = self._app_config.get("ui", {}).get("colors", {})
        chat_config = self._app_config.get("ui", {}).get("chat", {})
        
        return f"""
        <style>
        .chat-message {{
            padding: {chat_config.get("message_padding", "1.5rem")}; 
            border-radius: {chat_config.get("border_radius", "0.5rem")}; 
            margin-bottom: 1rem; 
            display: flex;
            flex-direction: column;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        .system-message {{
            background-color: {colors.get("system_message", {}).get("background", "#f0f2f6")};
            border-left: 5px solid {colors.get("system_message", {}).get("border", "#4e8cff")};
        }}
        .party-message {{
            background-color: {colors.get("party_message", {}).get("background", "#e6f3ff")};
            border-left: 5px solid {colors.get("party_message", {}).get("border", "#0068c9")};
        }}
        .politician-message {{
            background-color: {colors.get("politician_message", {}).get("background", "#f5f5f5")};
            border-left: 5px solid {colors.get("politician_message", {}).get("border", "#ff9500")};
        }}
        .message-header {{
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #333;
            font-size: 1.1em;
        }}
        .message-content {{
            margin-top: 0.5rem;
            white-space: pre-wrap;
            line-height: 1.5;
        }}
        .message-content p {{
            margin-bottom: 0.8rem;
        }}
        h4 {{
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #eee;
        }}
        </style>
        """
    
    def get_summary_box_style(self) -> str:
        """Get CSS style for summary box"""
        colors = self._app_config.get("ui", {}).get("colors", {})
        summary_colors = colors.get("summary_box", {})
        
        return f"""
        border: 2px solid {summary_colors.get("border", "#0068c9")}; 
        border-radius: 10px; 
        padding: 20px; 
        background-color: {summary_colors.get("background", "#f8f9fa")};
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
        margin-bottom: 30px;
        """
    
    def get_vote_tally_style(self) -> str:
        """Get CSS style for vote tally box"""
        colors = self._app_config.get("ui", {}).get("colors", {})
        tally_colors = colors.get("vote_tally", {})
        
        return f"""
        border: 1px solid {tally_colors.get("border", "#dee2e6")};
        border-radius: 8px;
        padding: 15px;
        background-color: {tally_colors.get("background", "#f8f9fa")};
        margin-top: 15px;
        margin-bottom: 15px;
        """
    
    def get_session_state_defaults(self) -> Dict[str, Any]:
        """Get default values for session state initialization"""
        session_defaults = self._app_config.get("session_defaults", {})
        
        defaults = {
            "simulation_created": session_defaults.get("simulation_created", False),
            "party_names": session_defaults.get("party_names", []),
            "party_abbreviations": session_defaults.get("party_abbreviations", []),
            "politicians_per_party": session_defaults.get("politicians_per_party", {}),
            "legislation_text": session_defaults.get("legislation_text", ""),
            "intra_party_results": session_defaults.get("intra_party_results"),
            "inter_party_results": session_defaults.get("inter_party_results"),
            "voting_results": session_defaults.get("voting_results"),
            "simulation_summary": session_defaults.get("simulation_summary"),
            "chat_messages": session_defaults.get("chat_messages", []),
            "model_name": self.llm_default_model,
            "temperature": self.llm_temperature_default,
            "max_tokens": self.llm_max_tokens_default,
            "num_parties": self.parliament_default_parties,
            "num_mps_per_party": self.parliament_default_mps,
            "default_party_data": {
                name: data["politicians"] 
                for name, data in self._default_parties.get("parties", {}).items()
            }
        }
        
        return defaults
    
    def validate_config(self) -> bool:
        """Validate configuration settings"""
        try:
            # Validate LLM config
            if not self.llm_available_models:
                return False
            if self.llm_default_model not in self.llm_available_models:
                return False
            
            temp_min, temp_max = self.llm_temperature_range
            if not (temp_min <= self.llm_temperature_default <= temp_max):
                return False
            
            tokens_min, tokens_max = self.llm_max_tokens_range
            if not (tokens_min <= self.llm_max_tokens_default <= tokens_max):
                return False
            
            # Validate Parliament config
            parties_min, parties_max = self.parliament_parties_range
            if not (parties_min <= self.parliament_default_parties <= parties_max):
                return False
            
            mps_min, mps_max = self.parliament_mps_range
            if not (mps_min <= self.parliament_default_mps <= mps_max):
                return False
            
            # Validate default parties data
            if not self._default_parties.get("parties"):
                return False
            
            return True
        except Exception as e:
            print(f"Configuration validation error: {e}")
            return False
    
    def save_config_changes(self, config_type: str, changes: Dict[str, Any]):
        """Save configuration changes back to YAML files"""
        try:
            if config_type == "app":
                file_path = self.config_dir / "app_config.yml"
                self._app_config.update(changes)
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(self._app_config, f, default_flow_style=False, allow_unicode=True)
            
            elif config_type == "texts":
                file_path = self.config_dir / "texts.yml"
                self._texts.update(changes)
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(self._texts, f, default_flow_style=False, allow_unicode=True)
            
            elif config_type == "parties":
                file_path = self.config_dir / "default_parties.yml"
                self._default_parties.update(changes)
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(self._default_parties, f, default_flow_style=False, allow_unicode=True)
                    
        except Exception as e:
            print(f"Error saving configuration: {e}")


# Global config instance
config = ConfigManager()