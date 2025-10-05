"""
MCP Dialog UI for Fusion 360
"""

import adsk.core
import adsk.fusion
import json
import threading
import traceback


class MCPDialog:
    """Dialog for MCP interaction"""

    def __init__(self, app, ui, mcp_client, action_executor):
        self.app = app
        self.ui = ui
        self.mcp_client = mcp_client
        self.action_executor = action_executor
        self.palette = None

        # Model selection
        self.selected_provider = "openai"
        self.selected_model = "gpt-4o-mini"

    def show(self):
        """Show the MCP dialog"""
        try:
            # Create palette
            self.palette = self.ui.palettes.itemById('MCPPalette')
            if not self.palette:
                self.palette = self.ui.palettes.add(
                    'MCPPalette',
                    'MCP Assistant',
                    'MCPPalette.html',
                    True,
                    True,
                    True,
                    800,
                    600
                )

            # Show palette
            self.palette.isVisible = True

        except:
            self.ui.messageBox('Failed to show dialog:\n{}'.format(traceback.format_exc()))

    def close(self):
        """Close the dialog"""
        if self.palette:
            self.palette.isVisible = False

    def process_prompt(self, prompt: str):
        """
        Process user prompt through MCP

        Args:
            prompt: User input prompt
        """
        def worker():
            try:
                # Get design context
                context = self._get_design_context()

                # Build MCP command
                command = {
                    "command": "ask_model",
                    "params": {
                        "provider": self.selected_provider,
                        "model": self.selected_model,
                        "prompt": prompt,
                        "temperature": 0.7
                    },
                    "context": context
                }

                # Send to MCP server
                response = self.mcp_client.send_command(command)

                # Execute actions
                if response.get("status") == "success":
                    actions = response.get("actions_to_execute", [])
                    for action in actions:
                        success = self.action_executor.execute(action)
                        if not success:
                            self._log(f"Failed to execute action: {action.get('action')}")
                        else:
                            self._log(f"✓ Executed: {action.get('explanation', action.get('action'))}")
                else:
                    self._log(f"Error: {response.get('message')}")

            except Exception as e:
                self._log(f"Error processing prompt: {str(e)}")

        # Run in separate thread to avoid blocking UI
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()

    def _get_design_context(self) -> dict:
        """Get current design context from Fusion"""
        try:
            design = adsk.fusion.Design.cast(self.app.activeProduct)
            if not design:
                return {
                    "active_component": "None",
                    "units": "mm",
                    "design_state": "no_design"
                }

            # Get active component
            component = design.activeComponent
            component_name = component.name if component else "RootComponent"

            # Get units
            units_manager = design.unitsManager
            default_unit = units_manager.defaultLengthUnits

            # Count geometry
            body_count = component.bRepBodies.count if component else 0
            sketch_count = component.sketches.count if component else 0

            return {
                "active_component": component_name,
                "units": default_unit,
                "design_state": "has_geometry" if body_count > 0 else "empty",
                "geometry_count": {
                    "bodies": body_count,
                    "sketches": sketch_count
                }
            }

        except:
            return {
                "active_component": "Unknown",
                "units": "mm",
                "design_state": "error"
            }

    def _log(self, message: str):
        """Log message to Fusion console and UI"""
        # Log to Fusion console
        self.ui.messageBox(message)
