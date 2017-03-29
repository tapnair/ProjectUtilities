import adsk.core
import adsk.fusion
import traceback

import os

from os.path import expanduser

from .Fusion360Utilities.Fusion360Utilities import get_app_objects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase


def traverse_folder(data_folder, file_stats, folder_stats):
    for folder in data_folder.dataFolders:
        folder_stats.append(get_folder_stats(folder))
        file_stats, folder_stats = traverse_folder(folder, file_stats, folder_stats)

    # TODO handle drawings
    for data_file in data_folder.dataFiles:
        if data_file.fileExtension in ["f3d", "f2d"]:
            file_stats.append(get_stats(data_file))

    return file_stats, folder_stats


def get_stats(data_file):
    file_stat = {
        # "childReferences": data_file.childReferences,
        "createdBy": data_file.createdBy.userName,
        "description": data_file.description,
        "fileExtension": data_file.fileExtension,
        "hasChildReferences": str(data_file.hasChildReferences),
        "hasOutofDateChildReferences": str(data_file.hasOutofDateChildReferences),
        "hasParentReferences": str(data_file.hasParentReferences),
        "id": data_file.id,
        # "inUseBy": data_file.inUseBy.userName,
        # "isInUse": str(data_file.isInUse),
        "isValid": str(data_file.isValid),
        "lastUpdatedBy": data_file.lastUpdatedBy.userName,
        # "latestVersion": data_file.latestVersion,
        "latestVersionNumber": str(data_file.latestVersionNumber),
        "name": data_file.name,
        "objectType": data_file.objectType,
        "parentFolder": data_file.parentFolder.name,
        "parentProject": data_file.parentProject.name,
        # "parentReferences": data_file.parentReferences,
        "versionNumber": str(data_file.versionNumber),
        # "versions": data_file.versions
    }

    return file_stat


def dup_check(name):
    if os.path.exists(name):
        base, ext = os.path.splitext(name)
        base += '-dup'
        name = base + ext
        name = dup_check(name)
    return name


def get_folder_stats(data_folder):

    folder_stats = {
        "name": data_folder.name,
        "parentFolder": data_folder.parentFolder.name,
        "parentProject": data_folder.parentProject.name
    }

    return folder_stats


# Creates directory and returns file name for settings file
def get_file_path():

    app = adsk.core.Application.get()
    active_project = app.data.activeProject
    project_name = active_project.name

    # Get Home directory
    default_path = expanduser("~")
    default_path += '/ProjectUtilities/'
    default_path += project_name
    default_path += '/'

    # Create if doesn't exist
    if not os.path.exists(default_path):
        os.makedirs(default_path)

    return default_path


def save_data(file_name, stats):

    if len(stats) < 1:
        return False

    file_name = dup_check(file_name)

    output_file = open(file_name, 'w')

    data_headers = []

    for key in stats[0].keys():
        data_headers.append(key)

    for data_item in data_headers:
        output_file.write(data_item + ',')
    output_file.write('\n')

    for file_stat in stats:
        for data_item in data_headers:
            output_file.write(file_stat[data_item] + ',')
        output_file.write('\n')

    output_file.close()

    return True


class StatsCommand(Fusion360CommandBase):
    def on_preview(self, command, inputs, args, input_values):
        pass

    def on_destroy(self, command, inputs, reason, input_values):
        pass

    def on_input_changed(self, command_, command_inputs, changed_input, input_values):
        pass

    def on_execute(self, command, inputs, args, input_values):

        app = adsk.core.Application.get()

        file_stats = []
        folder_stats = []
        file_stats, folder_stats = traverse_folder(app.data.activeProject.rootFolder, file_stats, folder_stats)

        msg = ''

        msg += "Total Files: " + str(len(file_stats)) + '\n\n'

        msg += "Total Folders: " + str(len(folder_stats))

        get_app_objects()['ui'].messageBox(msg)

        path = input_values['output_path']
        save_data(path + "files.csv", file_stats)
        save_data(path + "folders.csv", folder_stats)

    def on_create(self, command, command_inputs):
        app = adsk.core.Application.get()

        # allProjects = app.data.dataProjects
        active_project = app.data.activeProject
        project_name = active_project.name

        project_select = command_inputs.addStringValueInput('project_select', "Project to Get Statistics: ",
                                                            project_name)
        project_select.isReadOnly = True

        default_path = get_file_path()

        command_inputs.addStringValueInput('output_path', "Output Directory: ", default_path)

