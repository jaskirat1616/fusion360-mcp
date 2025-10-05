"""
MCP Command Schema
Defines the structure of commands sent from Fusion 360 to the MCP server
"""

from typing import Any, Dict, Optional, Literal
from pydantic import BaseModel, Field


class DesignContext(BaseModel):
    """Context information about the current Fusion 360 design state"""
    active_component: str = Field(default="RootComponent", description="Active component name")
    units: str = Field(default="mm", description="Design units")
    design_state: str = Field(default="empty", description="Current design state")
    active_sketch: Optional[str] = Field(default=None, description="Active sketch name if any")
    material: Optional[str] = Field(default=None, description="Applied material")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="User parameters")
    geometry_count: Dict[str, int] = Field(default_factory=dict, description="Geometry counts")

    class Config:
        json_schema_extra = {
            "example": {
                "active_component": "RootComponent",
                "units": "mm",
                "design_state": "has_geometry",
                "geometry_count": {"bodies": 2, "sketches": 1}
            }
        }


class ModelParams(BaseModel):
    """Parameters for model selection and execution"""
    provider: Literal["ollama", "openai", "gemini", "claude"] = Field(
        description="LLM provider to use"
    )
    model: str = Field(description="Specific model name")
    prompt: str = Field(description="User prompt or instruction")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: Optional[int] = Field(default=2000, description="Maximum tokens to generate")

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "prompt": "Create a 20mm cube with rounded edges",
                "temperature": 0.7
            }
        }


class MCPCommand(BaseModel):
    """Main MCP command structure"""
    command: Literal[
        "ask_model",
        "suggest_action",
        "context_update",
        "execute_action",
        "validate_action",
        "list_models",
        "health_check"
    ] = Field(description="Command type")
    params: Optional[ModelParams] = Field(default=None, description="Model parameters")
    context: Optional[DesignContext] = Field(default=None, description="Design context")
    action_data: Optional[Dict[str, Any]] = Field(default=None, description="Action data for execution")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "command": "ask_model",
                "params": {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "prompt": "Design a mounting bracket"
                },
                "context": {
                    "active_component": "RootComponent",
                    "units": "mm",
                    "design_state": "empty"
                }
            }
        }
