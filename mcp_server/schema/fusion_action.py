"""
Fusion Action Schema
Defines structured JSON actions that Fusion 360 can execute
"""

from typing import Any, Dict, List, Optional, Literal, Union
from pydantic import BaseModel, Field


class ActionParams(BaseModel):
    """Base class for action parameters"""
    class Config:
        extra = "allow"


class CreateBoxParams(ActionParams):
    """Parameters for creating a box"""
    width: float = Field(gt=0, description="Box width")
    height: float = Field(gt=0, description="Box height")
    depth: float = Field(gt=0, description="Box depth")
    unit: str = Field(default="mm", description="Unit of measurement")
    position: Optional[Dict[str, float]] = Field(default=None, description="Position coordinates")


class CreateCylinderParams(ActionParams):
    """Parameters for creating a cylinder"""
    radius: float = Field(gt=0, description="Cylinder radius")
    height: float = Field(gt=0, description="Cylinder height")
    unit: str = Field(default="mm", description="Unit of measurement")
    position: Optional[Dict[str, float]] = Field(default=None, description="Position coordinates")


class CreateSphereParams(ActionParams):
    """Parameters for creating a sphere"""
    radius: float = Field(gt=0, description="Sphere radius")
    unit: str = Field(default="mm", description="Unit of measurement")
    position: Optional[Dict[str, float]] = Field(default=None, description="Position coordinates")


class CreateHoleParams(ActionParams):
    """Parameters for creating a hole"""
    diameter: float = Field(gt=0, description="Hole diameter")
    depth: Optional[float] = Field(default=None, description="Hole depth (None for through)")
    position: Dict[str, float] = Field(description="Hole position coordinates")
    unit: str = Field(default="mm", description="Unit of measurement")


class CreateSketchParams(ActionParams):
    """Parameters for creating a sketch"""
    plane: Literal["XY", "XZ", "YZ"] = Field(description="Sketch plane")
    shapes: List[Dict[str, Any]] = Field(description="List of shapes to draw")


class ExtrudeParams(ActionParams):
    """Parameters for extrusion"""
    profile: str = Field(description="Profile or sketch name")
    distance: float = Field(description="Extrude distance")
    operation: Literal["new", "join", "cut", "intersect"] = Field(default="new")
    unit: str = Field(default="mm", description="Unit of measurement")


class FilletParams(ActionParams):
    """Parameters for filleting edges"""
    edges: List[str] = Field(description="Edge identifiers")
    radius: float = Field(gt=0, description="Fillet radius")
    unit: str = Field(default="mm", description="Unit of measurement")


class ModifyParameterParams(ActionParams):
    """Parameters for modifying design parameters"""
    parameter_name: str = Field(description="Parameter name")
    value: Union[float, str, int] = Field(description="New parameter value")
    unit: Optional[str] = Field(default=None, description="Unit if applicable")


class ApplyMaterialParams(ActionParams):
    """Parameters for applying material"""
    material_name: str = Field(description="Material name")
    body: Optional[str] = Field(default=None, description="Body name (None for all)")


class FusionAction(BaseModel):
    """Main Fusion action structure"""
    action: str = Field(description="Action type (verb_noun format)")
    params: Dict[str, Any] = Field(description="Action parameters")
    explanation: Optional[str] = Field(default=None, description="Human-readable explanation")
    safety_checks: List[str] = Field(default_factory=list, description="Safety validations performed")
    dependencies: List[str] = Field(default_factory=list, description="Required prior actions")

    class Config:
        json_schema_extra = {
            "example": {
                "action": "create_box",
                "params": {
                    "width": 20,
                    "height": 10,
                    "depth": 5,
                    "unit": "mm"
                },
                "explanation": "Creating a rectangular box 20x10x5mm",
                "safety_checks": ["dimensions_positive", "units_valid"]
            }
        }


class ActionSequence(BaseModel):
    """Sequence of multiple actions"""
    actions: List[FusionAction] = Field(description="Ordered list of actions")
    total_steps: int = Field(description="Total number of steps")
    estimated_time_seconds: Optional[float] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "actions": [
                    {
                        "action": "create_box",
                        "params": {"width": 20, "height": 20, "depth": 5},
                        "explanation": "Create base plate"
                    },
                    {
                        "action": "create_hole",
                        "params": {"diameter": 5, "position": {"x": 10, "y": 10}},
                        "explanation": "Add mounting hole"
                    }
                ],
                "total_steps": 2
            }
        }
