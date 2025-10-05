"""
Fusion Actions Executor
Executes structured JSON actions in Fusion 360
"""

import adsk.core
import adsk.fusion
import traceback
import math


class FusionActionExecutor:
    """Executes MCP actions in Fusion 360"""

    def __init__(self, app, ui):
        self.app = app
        self.ui = ui

    def execute(self, action: dict) -> bool:
        """
        Execute a Fusion action

        Args:
            action: Action dictionary with 'action' and 'params'

        Returns:
            True if successful, False otherwise
        """
        try:
            action_type = action.get("action")
            params = action.get("params", {})

            # Route to appropriate handler
            if action_type == "create_box":
                return self._create_box(params)
            elif action_type == "create_cylinder":
                return self._create_cylinder(params)
            elif action_type == "create_sphere":
                return self._create_sphere(params)
            elif action_type == "create_hole":
                return self._create_hole(params)
            elif action_type == "extrude":
                return self._extrude(params)
            elif action_type == "fillet":
                return self._fillet(params)
            elif action_type == "apply_material":
                return self._apply_material(params)
            else:
                self.ui.messageBox(f"Unknown action type: {action_type}")
                return False

        except Exception as e:
            self.ui.messageBox(f'Action execution failed:\n{traceback.format_exc()}')
            return False

    def _create_box(self, params: dict) -> bool:
        """Create a box"""
        try:
            design = adsk.fusion.Design.cast(self.app.activeProduct)
            root_comp = design.rootComponent

            # Get parameters
            width = self._convert_to_cm(params.get("width"), params.get("unit", "mm"))
            height = self._convert_to_cm(params.get("height"), params.get("unit", "mm"))
            depth = self._convert_to_cm(params.get("depth"), params.get("unit", "mm"))

            # Create sketch on XY plane
            sketches = root_comp.sketches
            xy_plane = root_comp.xYConstructionPlane
            sketch = sketches.add(xy_plane)

            # Draw rectangle
            lines = sketch.sketchCurves.sketchLines
            rect_lines = lines.addTwoPointRectangle(
                adsk.core.Point3D.create(0, 0, 0),
                adsk.core.Point3D.create(width, depth, 0)
            )

            # Get profile
            profile = sketch.profiles.item(0)

            # Create extrude
            extrudes = root_comp.features.extrudeFeatures
            distance = adsk.core.ValueInput.createByReal(height)
            extrude = extrudes.addSimple(
                profile,
                distance,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )

            return True

        except Exception as e:
            self.ui.messageBox(f'Box creation failed:\n{str(e)}')
            return False

    def _create_cylinder(self, params: dict) -> bool:
        """Create a cylinder"""
        try:
            design = adsk.fusion.Design.cast(self.app.activeProduct)
            root_comp = design.rootComponent

            # Get parameters
            radius = self._convert_to_cm(params.get("radius"), params.get("unit", "mm"))
            height = self._convert_to_cm(params.get("height"), params.get("unit", "mm"))

            # Create sketch on XY plane
            sketches = root_comp.sketches
            xy_plane = root_comp.xYConstructionPlane
            sketch = sketches.add(xy_plane)

            # Draw circle
            circles = sketch.sketchCurves.sketchCircles
            center = adsk.core.Point3D.create(0, 0, 0)
            circle = circles.addByCenterRadius(center, radius)

            # Get profile
            profile = sketch.profiles.item(0)

            # Create extrude
            extrudes = root_comp.features.extrudeFeatures
            distance = adsk.core.ValueInput.createByReal(height)
            extrude = extrudes.addSimple(
                profile,
                distance,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )

            return True

        except Exception as e:
            self.ui.messageBox(f'Cylinder creation failed:\n{str(e)}')
            return False

    def _create_sphere(self, params: dict) -> bool:
        """Create a sphere using revolve"""
        try:
            design = adsk.fusion.Design.cast(self.app.activeProduct)
            root_comp = design.rootComponent

            # Get parameters
            radius = self._convert_to_cm(params.get("radius"), params.get("unit", "mm"))

            # Create sketch on XZ plane
            sketches = root_comp.sketches
            xz_plane = root_comp.xZConstructionPlane
            sketch = sketches.add(xz_plane)

            # Draw semicircle arc and axis
            lines = sketch.sketchCurves.sketchLines
            arcs = sketch.sketchCurves.sketchArcs

            # Center point
            center = adsk.core.Point3D.create(0, 0, 0)

            # Axis line
            axis_line = lines.addByTwoPoints(
                adsk.core.Point3D.create(0, -radius - 1, 0),
                adsk.core.Point3D.create(0, radius + 1, 0)
            )

            # Arc for half circle
            arc = arcs.addByCenterStartSweep(
                center,
                adsk.core.Point3D.create(0, radius, 0),
                math.pi
            )

            # Close with line
            close_line = lines.addByTwoPoints(
                arc.endSketchPoint,
                arc.startSketchPoint
            )

            # Get profile
            profile = sketch.profiles.item(0)

            # Create revolve
            revolves = root_comp.features.revolveFeatures
            revolve_input = revolves.createInput(
                profile,
                axis_line,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            angle = adsk.core.ValueInput.createByReal(2 * math.pi)
            revolve_input.setAngleExtent(False, angle)
            revolve = revolves.add(revolve_input)

            return True

        except Exception as e:
            self.ui.messageBox(f'Sphere creation failed:\n{str(e)}')
            return False

    def _create_hole(self, params: dict) -> bool:
        """Create a hole"""
        try:
            design = adsk.fusion.Design.cast(self.app.activeProduct)
            root_comp = design.rootComponent

            # Get parameters
            diameter = self._convert_to_cm(params.get("diameter"), params.get("unit", "mm"))
            depth = params.get("depth")
            if depth:
                depth = self._convert_to_cm(depth, params.get("unit", "mm"))

            position = params.get("position", {"x": 0, "y": 0, "z": 0})
            x = self._convert_to_cm(position.get("x", 0), params.get("unit", "mm"))
            y = self._convert_to_cm(position.get("y", 0), params.get("unit", "mm"))

            # Create sketch on XY plane
            sketches = root_comp.sketches
            xy_plane = root_comp.xYConstructionPlane
            sketch = sketches.add(xy_plane)

            # Draw circle at position
            circles = sketch.sketchCurves.sketchCircles
            center = adsk.core.Point3D.create(x, y, 0)
            circle = circles.addByCenterRadius(center, diameter / 2)

            # Get profile
            profile = sketch.profiles.item(0)

            # Create extrude (cut operation)
            extrudes = root_comp.features.extrudeFeatures
            if depth:
                distance = adsk.core.ValueInput.createByReal(depth)
            else:
                distance = adsk.core.ValueInput.createByReal(10)  # Default depth

            extrude = extrudes.addSimple(
                profile,
                distance,
                adsk.fusion.FeatureOperations.CutFeatureOperation
            )

            return True

        except Exception as e:
            self.ui.messageBox(f'Hole creation failed:\n{str(e)}')
            return False

    def _extrude(self, params: dict) -> bool:
        """Create extrusion from existing profile"""
        # This would require selecting an existing sketch/profile
        # Implementation depends on workflow
        self.ui.messageBox("Extrude action requires manual implementation")
        return False

    def _fillet(self, params: dict) -> bool:
        """Apply fillet to edges"""
        # This would require edge selection
        # Implementation depends on workflow
        self.ui.messageBox("Fillet action requires manual implementation")
        return False

    def _apply_material(self, params: dict) -> bool:
        """Apply material to body"""
        try:
            design = adsk.fusion.Design.cast(self.app.activeProduct)
            material_name = params.get("material_name")

            # Get material library
            materials = self.app.materialLibraries

            # Search for material
            for lib in materials:
                for mat in lib.materials:
                    if material_name.lower() in mat.name.lower():
                        # Apply to all bodies or specific body
                        root_comp = design.rootComponent
                        for body in root_comp.bRepBodies:
                            body.material = mat
                        return True

            self.ui.messageBox(f"Material '{material_name}' not found")
            return False

        except Exception as e:
            self.ui.messageBox(f'Material application failed:\n{str(e)}')
            return False

    def _convert_to_cm(self, value: float, unit: str) -> float:
        """
        Convert value to cm (Fusion's internal unit)

        Args:
            value: Numerical value
            unit: Unit string (mm, cm, m, in, ft)

        Returns:
            Value in cm
        """
        conversions = {
            "mm": 0.1,
            "cm": 1.0,
            "m": 100.0,
            "in": 2.54,
            "ft": 30.48
        }
        return value * conversions.get(unit.lower(), 1.0)
