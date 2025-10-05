"""
Configuration loader with environment variable support
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class ModelConfig(BaseModel):
    """Configuration for a specific model provider"""
    available: List[str] = Field(default_factory=list)
    default: str


class Config(BaseSettings):
    """Main configuration class"""
    # API Configuration
    ollama_url: str = Field(default="http://localhost:11434")
    openai_api_key: Optional[str] = Field(default=None)
    gemini_api_key: Optional[str] = Field(default=None)
    claude_api_key: Optional[str] = Field(default=None)

    # Server Configuration
    mcp_host: str = Field(default="127.0.0.1")
    mcp_port: int = Field(default=9000)
    allow_remote: bool = Field(default=False)

    # Model Configuration
    default_model: str = Field(default="openai:gpt-4o-mini")
    fallback_chain: List[str] = Field(default_factory=list)

    # Logging
    log_level: str = Field(default="INFO")
    log_dir: str = Field(default="logs")

    # Cache
    cache_enabled: bool = Field(default=True)
    cache_type: str = Field(default="json")
    cache_path: str = Field(default="context_cache.json")

    # Timeouts and Retries
    timeout_seconds: int = Field(default=30)
    max_retries: int = Field(default=3)
    retry_delay: float = Field(default=1.0)

    # Model-specific configs
    models: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from file and environment

    Args:
        config_path: Path to config.json file

    Returns:
        Config object
    """
    # Load environment variables
    load_dotenv()

    # Start with default config
    config_data = {}

    # Try to load from file
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            config_data = json.load(f)
    elif Path("config.json").exists():
        with open("config.json", 'r') as f:
            config_data = json.load(f)

    # Override with environment variables
    env_overrides = {
        "ollama_url": os.getenv("OLLAMA_URL"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "claude_api_key": os.getenv("CLAUDE_API_KEY"),
        "mcp_host": os.getenv("MCP_HOST"),
        "mcp_port": os.getenv("MCP_PORT"),
        "log_level": os.getenv("LOG_LEVEL"),
    }

    # Apply non-None overrides
    for key, value in env_overrides.items():
        if value is not None:
            config_data[key] = value

    # Create and return config
    config = Config(**config_data)

    return config


def get_model_config(config: Config, provider: str) -> Optional[Dict[str, Any]]:
    """
    Get model configuration for a specific provider

    Args:
        config: Main config object
        provider: Provider name (ollama, openai, gemini, claude)

    Returns:
        Model config dictionary or None
    """
    return config.models.get(provider)
