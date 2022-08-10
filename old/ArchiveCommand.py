import adsk.core
import adsk.fusion
import traceback

import os

from os.path import expanduser

from .Fusion360Utilities.Fusion360Utilities import get_app_objects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase


def export_folder(root_folder, output_folder, file_types, write_version):

    for folder in root_folder.dataFolders:

        new_output_folder = os.path.join(output_folder, folder.name, "")

        # Create if doesn't exist
        if not os.path.exists(new_output_folder):
            os.makedirs(new_output_folder)
        export_folder(folder, new_output_folder, file_types, write_version)

    for file in root_folder.dataFiles:
        if file.fileExtension == "f3d":
            open_doc(file, output_folder, file_types, write_version)


def dup_check(name):
    if os.path.exists(name):
        base, ext = os.path.splitext(name)
        base += '-dup'
        name = base + ext
        dup_check(name)
    return name


# Creates directory and returns file name for settings file
def get_default_folder(project_name):
    # Get user's home directory
    default_dir = expanduser("~")

    # Create a subdirectory for this application settings
    default_dir = os.path.join(default_dir, 'ProjectUtilities', "")

    # Create the folder if it does not exist
    if not os.path.exists(default_dir):
        os.makedirs(default_dir)

    # Create a subdirectory for this application settings
    project_dir = os.path.join(default_dir, project_name, "")

    # Create the folder if it does not exist
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    return project_dir


def export_active_doc(output_folder, file_types, write_version):
    app = adsk.core.Application.get()
    design = app.activeProduct
    export_mgr = design.exportManager

    export_functions = [export_mgr.createIGESExportOptions,
                        export_mgr.createSTEPExportOptions,
                        export_mgr.createSATExportOptions,
                        export_mgr.createSMTExportOptions,
                        export_mgr.createFusionArchiveExportOptions,
                        export_mgr.createSTLExportOptions]
    export_extensions = ['.igs', '.step', '.sat', '.smt', '.f3d', '.stl']

    for i in range(file_types.count):

        if file_types.item(i).isSelected:

            doc_name = app.activeDocument.name

            if not write_version:
                doc_name = doc_name[:doc_name.rfind(' v')]

            export_doc_name = doc_name + export_extensions[i]
            export_name = os.path.join(output_folder, export_doc_name)
            export_name = dup_check(export_name)
            export_options = export_functions[i](export_name)
            export_mgr.execute(export_options)

            # get_app_objects()['ui'].messageBox(export_name)


def open_doc(data_file, output_folder, file_types, write_version):
    app = adsk.core.Application.get()

    try:
        document = app.documents.open(data_file, True)
        if document is not None:
            document.activate()
            export_active_doc(output_folder, file_types, write_version)

    except:
        pass


class ArchiveCommand(Fusion360CommandBase):
    def on_preview(self, command, inputs, args, input_values):
        pass

    def on_destroy(self, command, inputs, reason, input_values):
        pass

    def on_input_changed(self, command_, command_inputs, changed_input, input_values):
        pass

    def on_execute(self, command, inputs, args, input_values):
        # Get the values from the user input
        output_path = inputs.itemById('output_path').value
        file_types = inputs.itemById('file_type_input').listItems

        app = adsk.core.Application.get()
        write_version = inputs.itemById('write_version').value

        export_folder(app.data.activeProject.rootFolder, output_path, file_types, write_version)

        close_command = get_app_objects()['ui'].commandDefinitions.itemById('cmdID_Close_Docs')
        close_command.execute()

    def on_create(self, command, command_inputs):
        app = adsk.core.Application.get()

        active_project = app.data.activeProject
        project_name = active_project.name

        project_select = command_inputs.addStringValueInput('project_select', "Project to Archive: ", project_name)
        project_select.isReadOnly = True

        default_path = get_default_folder(project_name)
        command_inputs.addStringValueInput('output_path', 'Output Path: ', default_path)

        drop_input_list = command_inputs.addDropDownCommandInput('file_type_input', 'Export Types',
                                                                 adsk.core.DropDownStyles.CheckBoxDropDownStyle)

        drop_input_list = drop_input_list.listItems
        drop_input_list.add('IGES', False)
        drop_input_list.add('STEP', True)
        drop_input_list.add('SAT', False)
        drop_input_list.add('SMT', False)
        drop_input_list.add('F3D', False)
        drop_input_list.add('STL', False)

        command_inputs.addBoolValueInput('write_version', 'Write versions to output file names?', True)


