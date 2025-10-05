"""
Tests for Configuration Loader
"""

import pytest
import json
from pathlib import Path
from mcp_server.utils import load_config, Config


def test_default_config():
    """Test default configuration"""
    config = Config()
    assert config.mcp_host == "127.0.0.1"
    assert config.mcp_port == 9000
    assert config.timeout_seconds == 30
    assert config.max_retries == 3


def test_config_from_dict():
    """Test configuration from dictionary"""
    config_data = {
        "mcp_host": "0.0.0.0",
        "mcp_port": 8080,
        "openai_api_key": "test_key"
    }
    config = Config(**config_data)
    assert config.mcp_host == "0.0.0.0"
    assert config.mcp_port == 8080
    assert config.openai_api_key == "test_key"


def test_config_validation():
    """Test configuration validation"""
    # Valid port
    config = Config(mcp_port=9000)
    assert config.mcp_port == 9000

    # Test retry values
    config = Config(max_retries=5)
    assert config.max_retries == 5


def test_load_config_missing_file():
    """Test loading config when file doesn't exist"""
    # Should return default config if file missing
    config = load_config("nonexistent.json")
    assert config is not None
    assert isinstance(config, Config)
