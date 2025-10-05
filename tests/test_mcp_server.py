"""
Tests for MCP Server
"""

import pytest
from fastapi.testclient import TestClient
from mcp_server.server import app
from mcp_server.schema import MCPCommand, ModelParams


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "providers" in data


def test_mcp_command_ask_model(client):
    """Test ask_model command"""
    command = {
        "command": "ask_model",
        "params": {
            "provider": "ollama",
            "model": "llama3",
            "prompt": "Create a 20mm cube",
            "temperature": 0.7
        },
        "context": {
            "active_component": "RootComponent",
            "units": "mm",
            "design_state": "empty"
        }
    }

    response = client.post("/mcp/command", json=command)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["success", "error", "clarification_needed"]


def test_list_models(client):
    """Test list models endpoint"""
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data


def test_history_endpoint(client):
    """Test history endpoint"""
    response = client.get("/history?limit=5")
    # May return 503 if cache not enabled
    assert response.status_code in [200, 503]


def test_invalid_command(client):
    """Test invalid command handling"""
    command = {
        "command": "invalid_command",
        "params": None
    }

    response = client.post("/mcp/command", json=command)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
