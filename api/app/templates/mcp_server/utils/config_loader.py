"""
Configuration loading utilities for MCP server.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Configuration loader for MCP server tools"""
    
    @staticmethod
    def load_tools_config(config_path: str) -> Dict[str, Any]:
        """Load tools configuration from JSON file"""
        config_path_obj = Path(config_path)
        
        if not config_path_obj.is_absolute():
            # Resolve path relative to the current working directory or script directory
            script_dir = Path(__file__).parent.parent
            config_path_obj = script_dir / config_path
        
        if not config_path_obj.exists():
            raise FileNotFoundError(f"Tools configuration file not found: {config_path_obj}")
        
        logger.info(f"Loading tools config from: {config_path_obj}")
        
        with open(config_path_obj, 'r') as f:
            config = json.load(f)
        
        # Validate required fields
        if "api_name" not in config:
            raise ValueError("Configuration missing required field: api_name")
        
        if "tools" not in config:
            config["tools"] = []
        
        if "composite_tools" not in config:
            config["composite_tools"] = []
        
        logger.info(f"Loaded config for API: {config['api_name']}")
        logger.info(f"Standard tools: {len(config['tools'])} | Composite tools: {len(config['composite_tools'])}")
        
        return config
    
    @staticmethod
    def get_environment_config() -> Dict[str, str]:
        """Get environment configuration"""
        return {
            "api_key": os.getenv("API_KEY", ""),
            "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY", ""),
            "tools_config_path": os.getenv("TOOLS_CONFIG_PATH", "tools.json")
        }