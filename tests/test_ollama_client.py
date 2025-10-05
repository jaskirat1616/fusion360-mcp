"""
Tests for Ollama Client
"""

import pytest
from mcp_server.llm_clients import OllamaClient


@pytest.mark.asyncio
async def test_ollama_client_init():
    """Test Ollama client initialization"""
    client = OllamaClient(base_url="http://localhost:11434", timeout=30)
    assert client.base_url == "http://localhost:11434"
    assert client.timeout == 30


@pytest.mark.asyncio
async def test_ollama_parse_json():
    """Test JSON parsing from text"""
    client = OllamaClient()

    # Test direct JSON
    text = '{"action": "create_box", "params": {"width": 20}}'
    result = client._parse_json(text)
    assert result is not None
    assert result["action"] == "create_box"

    # Test JSON embedded in text
    text = 'Here is the action: {"action": "create_box", "params": {"width": 20}} done'
    result = client._parse_json(text)
    assert result is not None
    assert result["action"] == "create_box"

    # Test invalid JSON
    text = 'This is not JSON at all'
    result = client._parse_json(text)
    assert result is None


@pytest.mark.asyncio
async def test_ollama_list_models():
    """Test listing Ollama models"""
    client = OllamaClient()
    # This will fail if Ollama is not running, which is okay for tests
    models = await client.list_models()
    assert isinstance(models, list)
