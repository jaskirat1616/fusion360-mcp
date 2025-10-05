"""
LLM Response Schema
Unified response structure from all LLM providers
"""

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

from .fusion_action import FusionAction, ActionSequence


class LLMResponseMetadata(BaseModel):
    """Metadata about the LLM response"""
    provider: Literal["ollama", "openai", "gemini", "claude"] = Field(description="Provider name")
    model: str = Field(description="Model name")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    tokens_used: Optional[int] = Field(default=None, description="Tokens consumed")
    latency_ms: Optional[float] = Field(default=None, description="Response latency")
    temperature: Optional[float] = Field(default=None, description="Temperature used")


class LLMError(BaseModel):
    """Error structure for LLM failures"""
    type: str = Field(description="Error type (timeout, api_error, validation_error, etc.)")
    message: str = Field(description="Error message")
    provider: str = Field(description="Provider that failed")
    retry_count: int = Field(default=0, description="Number of retries attempted")
    recoverable: bool = Field(default=True, description="Whether error is recoverable")


class ClarifyingQuestion(BaseModel):
    """Structure for questions when user intent is ambiguous"""
    question: str = Field(description="The clarifying question")
    context: str = Field(description="Why this question is needed")
    suggestions: List[str] = Field(default_factory=list, description="Suggested answers")


class LLMResponse(BaseModel):
    """Unified LLM response structure"""
    success: bool = Field(description="Whether the response was successful")
    provider: str = Field(description="Provider name")
    model: str = Field(description="Model name")
    raw_output: str = Field(description="Raw text output from model")
    action: Optional[FusionAction] = Field(default=None, description="Parsed Fusion action")
    action_sequence: Optional[ActionSequence] = Field(default=None, description="Multiple actions")
    clarifying_questions: List[ClarifyingQuestion] = Field(
        default_factory=list,
        description="Questions for ambiguous requests"
    )
    reasoning: Optional[str] = Field(default=None, description="Model's reasoning process")
    metadata: LLMResponseMetadata = Field(description="Response metadata")
    error: Optional[LLMError] = Field(default=None, description="Error if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "provider": "openai",
                "model": "gpt-4o-mini",
                "raw_output": "I'll create a 20mm cube...",
                "action": {
                    "action": "create_box",
                    "params": {"width": 20, "height": 20, "depth": 20, "unit": "mm"},
                    "explanation": "Creating a 20mm cube as requested"
                },
                "metadata": {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "tokens_used": 150,
                    "latency_ms": 1200
                }
            }
        }


class MCPResponse(BaseModel):
    """Response sent back to Fusion 360"""
    status: Literal["success", "error", "clarification_needed", "partial"] = Field(
        description="Response status"
    )
    llm_response: Optional[LLMResponse] = Field(default=None, description="LLM response data")
    message: str = Field(description="Human-readable status message")
    actions_to_execute: List[FusionAction] = Field(
        default_factory=list,
        description="Actions ready for execution"
    )
    warnings: List[str] = Field(default_factory=list, description="Warning messages")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Action generated successfully",
                "actions_to_execute": [
                    {
                        "action": "create_box",
                        "params": {"width": 20, "height": 20, "depth": 20},
                        "explanation": "Creating cube"
                    }
                ],
                "llm_response": {
                    "success": True,
                    "provider": "openai",
                    "model": "gpt-4o-mini"
                }
            }
        }
