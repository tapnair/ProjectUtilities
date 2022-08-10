# Author-Patrick Rainsberry
# Description-Set of Utilities for Managing Fusion 360 Projects

from .ArchiveCommand import ArchiveCommand
from .StatsCommand import StatsCommand
from .CloseAllCommand import CloseAllCommand

commands = []
command_definitions = []

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Archive Project',
    'cmd_description': 'Export All files from Current Fusion 360 Project',
    'cmd_id': 'cmdID_ProjectUtilities_Archive',
    'cmd_resources': './resources/Archive',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'SolidScriptsAddinsPanel',
    'class': ArchiveCommand
}
command_definitions.append(cmd)

# Define parameters for 2nd command
cmd = {
    'cmd_name': 'Project Statistics',
    'cmd_description': 'Get Statistics about current Fusion 360 Project',
    'cmd_id': 'cmdID_ProjectUtilities_Statistics',
    'cmd_resources': './resources/Icons',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'SolidScriptsAddinsPanel',
    'class': StatsCommand
}
command_definitions.append(cmd)

# Define parameters for 3rd command
cmd = {
    'cmd_name': 'Close All Documents',
    'cmd_description': 'NOTE: This closes all documents WITHOUT prompting to save',
    'cmd_id': 'cmdID_Close_Docs',
    'cmd_resources': './resources/Icons',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'SolidScriptsAddinsPanel',
    'command_visible': True,
    'class': CloseAllCommand
}
command_definitions.append(cmd)

# Set to True to display various useful messages when debugging your app
debug = False


# Don't change anything below here:
for cmd_def in command_definitions:
    command = cmd_def['class'](cmd_def, debug)
    commands.append(command)


def run(context):
    for run_command in commands:
        run_command.on_run()


def stop(context):
    for stop_command in commands:
        stop_command.on_stop()
