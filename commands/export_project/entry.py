import adsk.core
import os

from ...lib.projectUtils import export_project, clean_up_export_utils, get_folder_dialog
from ...lib import fusion360utils as futil
from ... import config

app = adsk.core.Application.get()
ui = app.userInterface

CMD_NAME = 'Export Project'
CMD_Description = 'Export All Data from a Project'

IS_PROMOTED = True
COMMAND_BESIDE_ID = ''

WORKSPACE_ID = config.design_workspace
TAB_ID = config.utilities_tab_id
TAB_NAME = config.utilities_tab_name

PANEL_NAME = config.project_utilities_panel_name
PANEL_AFTER = config.project_utilities_panel_after
PANEL_ID = config.project_utilities_panel_id

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_{CMD_NAME}'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')
local_handlers = []


# Executed when add-in is run.
def start():
    command_cleanup()

    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get target toolbar tab for the command and create the tab if necessary.
    toolbar_tab = workspace.toolbarTabs.itemById(TAB_ID)
    if toolbar_tab is None:
        toolbar_tab = workspace.toolbarTabs.add(TAB_ID, TAB_NAME)

    # Get target panel for the command and and create the panel if necessary.
    panel = toolbar_tab.toolbarPanels.itemById(PANEL_ID)
    if panel is None:
        panel = toolbar_tab.toolbarPanels.add(PANEL_ID, PANEL_NAME, PANEL_AFTER, False)

    # Create the button command control in the UI after the specified existing command.
    if len(COMMAND_BESIDE_ID) > 0:
        control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)
    else:
        control = panel.controls.addCommand(cmd_def)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


def command_cleanup():
    # Delete the command control
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    if workspace:
        panel = workspace.toolbarPanels.itemById(PANEL_ID)
        if panel:
            command_control = panel.controls.itemById(CMD_ID)
            if command_control:
                command_control.deleteMe()

    # Delete the command definition
    command_definition = ui.commandDefinitions.itemById(CMD_ID)
    if command_definition:
        command_definition.deleteMe()


# Executed when add-in is stopped.
def stop():
    command_cleanup()
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Delete the panel if it is empty
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    if panel.controls.count == 0:
        panel.deleteMe()

    # Delete the tab if it is empty
    toolbar_tab = workspace.toolbarTabs.itemById(TAB_ID)
    if toolbar_tab.toolbarPanels.count == 0:
        toolbar_tab.deleteMe()

    clean_up_export_utils()


def command_created(args: adsk.core.CommandCreatedEventArgs):
    # Folder picker dialog will be shown before command dialog
    initial_path = get_folder_dialog()

    inputs = args.command.commandInputs
    inputs.addStringValueInput('TARGET_FOLDER', 'Location', initial_path)

    # TODO Add browse button?

    inputs.addBoolValueInput('SKIP_EXPORT_ON_PARENTS', 'Skip Export of Child Components', True, '',
                             config.SKIP_EXPORT_ON_PARENTS)
    inputs.addBoolValueInput('SKIP_EXPORT_ON_DUPLICATES', 'Skip Export of duplicates in target directory', True, '',
                             config.SKIP_EXPORT_ON_DUPLICATES)
    inputs.addBoolValueInput('AUTO_SHOW_TEXT_COMMANDS', 'Show Output in Text Command Dialog?', True, '',
                             config.AUTO_SHOW_TEXT_COMMANDS)

    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def command_execute(args: adsk.core.CommandEventArgs):
    inputs = args.command.commandInputs
    target_folder_input: adsk.core.StringValueCommandInput = inputs.itemById('TARGET_FOLDER')
    skip_export_on_parents_input: adsk.core.BoolValueCommandInput = inputs.itemById('SKIP_EXPORT_ON_PARENTS')
    skip_export_on_duplicates_input: adsk.core.BoolValueCommandInput = inputs.itemById('SKIP_EXPORT_ON_DUPLICATES')
    auto_show_text_commands_input: adsk.core.BoolValueCommandInput = inputs.itemById('AUTO_SHOW_TEXT_COMMANDS')

    target_folder = target_folder_input.value
    skip_export_on_parents = skip_export_on_parents_input.value
    skip_export_on_duplicates = skip_export_on_duplicates_input.value
    auto_show_text_commands = auto_show_text_commands_input.value

    if auto_show_text_commands:
        textPalette = ui.palettes.itemById('TextCommands')
        if not textPalette.isVisible:
            textPalette.isVisible = True

    export_project(target_folder, skip_export_on_parents, skip_export_on_duplicates)


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs


def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
