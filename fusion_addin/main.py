"""
Fusion 360 MCP Add-in
Main entry point for the Fusion 360 integration
"""

import adsk.core
import adsk.fusion
import traceback
import threading
import json

from .ui_dialog import MCPDialog
from .fusion_actions import FusionActionExecutor
from .utils.network import MCPClient


# Global instances
app = None
ui = None
handlers = []
mcp_client = None
action_executor = None
dialog = None
command = None


def run(context):
    """Entry point when add-in starts"""
    global app, ui, mcp_client, action_executor

    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Initialize MCP client
        mcp_client = MCPClient(host="127.0.0.1", port=9000)

        # Initialize action executor
        action_executor = FusionActionExecutor(app, ui)

        # Create command
        create_command()

        ui.messageBox('FusionMCP Add-in Started!\nUse the "MCP Assistant" command to interact with AI models.')

    except:
        if ui:
            ui.messageBox('Failed to start FusionMCP:\n{}'.format(traceback.format_exc()))


def stop(context):
    """Entry point when add-in stops"""
    global ui, command, handlers

    try:
        if command:
            command.deleteMe()

        # Clean up handlers
        handlers.clear()

        if ui:
            ui.messageBox('FusionMCP Add-in Stopped')

    except:
        if ui:
            ui.messageBox('Failed to stop FusionMCP:\n{}'.format(traceback.format_exc()))


def create_command():
    """Create the MCP Assistant command"""
    global ui, command, handlers

    try:
        # Get the ADD-INS panel in the model workspace
        workspace = ui.workspaces.itemById('FusionSolidEnvironment')
        panel = workspace.toolbarPanels.itemById('SolidScriptsAddinsPanel')

        # Create command definition
        cmd_def = ui.commandDefinitions.itemById('FusionMCPCommand')
        if not cmd_def:
            cmd_def = ui.commandDefinitions.addButtonDefinition(
                'FusionMCPCommand',
                'MCP Assistant',
                'AI-powered parametric design assistant',
                ''
            )

        # Add command created event handler
        on_command_created = MCPCommandCreatedHandler()
        cmd_def.commandCreated.add(on_command_created)
        handlers.append(on_command_created)

        # Add button to panel
        control = panel.controls.itemById('FusionMCPCommand')
        if not control:
            panel.controls.addCommand(cmd_def)

        command = cmd_def

    except:
        if ui:
            ui.messageBox('Failed to create command:\n{}'.format(traceback.format_exc()))


class MCPCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """Handler for when command is created"""

    def __init__(self):
        super().__init__()

    def notify(self, args):
        global handlers, dialog

        try:
            cmd = args.command

            # Create dialog
            dialog = MCPDialog(app, ui, mcp_client, action_executor)

            # Add execute event handler
            on_execute = MCPCommandExecuteHandler()
            cmd.execute.add(on_execute)
            handlers.append(on_execute)

            # Add destroy event handler
            on_destroy = MCPCommandDestroyHandler()
            cmd.destroy.add(on_destroy)
            handlers.append(on_destroy)

            # Show dialog
            dialog.show()

        except:
            ui.messageBox('Failed in command created handler:\n{}'.format(traceback.format_exc()))


class MCPCommandExecuteHandler(adsk.core.CommandEventHandler):
    """Handler for command execution"""

    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            # Dialog handles execution
            pass

        except:
            ui.messageBox('Failed in command execute handler:\n{}'.format(traceback.format_exc()))


class MCPCommandDestroyHandler(adsk.core.CommandEventHandler):
    """Handler for command destruction"""

    def __init__(self):
        super().__init__()

    def notify(self, args):
        global dialog

        try:
            if dialog:
                dialog.close()
                dialog = None

        except:
            ui.messageBox('Failed in command destroy handler:\n{}'.format(traceback.format_exc()))
