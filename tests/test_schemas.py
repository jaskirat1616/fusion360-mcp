"""
Tests for Pydantic Schemas
"""

import pytest
from mcp_server.schema import (
    MCPCommand,
    ModelParams,
    DesignContext,
    FusionAction,
    LLMResponse,
    MCPResponse
)


def test_design_context_schema():
    """Test DesignContext schema"""
    context = DesignContext(
        active_component="RootComponent",
        units="mm",
        design_state="empty"
    )
    assert context.active_component == "RootComponent"
    assert context.units == "mm"
    assert context.design_state == "empty"


def test_model_params_schema():
    """Test ModelParams schema"""
    params = ModelParams(
        provider="openai",
        model="gpt-4o-mini",
        prompt="Create a box",
        temperature=0.7
    )
    assert params.provider == "openai"
    assert params.model == "gpt-4o-mini"
    assert params.temperature == 0.7


def test_fusion_action_schema():
    """Test FusionAction schema"""
    action = FusionAction(
        action="create_box",
        params={"width": 20, "height": 20, "depth": 20, "unit": "mm"},
        explanation="Creating a 20mm cube"
    )
    assert action.action == "create_box"
    assert action.params["width"] == 20
    assert action.explanation == "Creating a 20mm cube"


def test_mcp_command_schema():
    """Test MCPCommand schema"""
    command = MCPCommand(
        command="ask_model",
        params=ModelParams(
            provider="openai",
            model="gpt-4o-mini",
            prompt="Test prompt"
        )
    )
    assert command.command == "ask_model"
    assert command.params.provider == "openai"


def test_mcp_response_schema():
    """Test MCPResponse schema"""
    response = MCPResponse(
        status="success",
        message="Action generated",
        actions_to_execute=[
            FusionAction(
                action="create_box",
                params={"width": 20},
                explanation="Test"
            )
        ]
    )
    assert response.status == "success"
    assert len(response.actions_to_execute) == 1
    assert response.actions_to_execute[0].action == "create_box"
