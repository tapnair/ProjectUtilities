#  Copyright 2022 by Autodesk, Inc.
#  Permission to use, copy, modify, and distribute this software in object code form
#  for any purpose and without fee is hereby granted, provided that the above copyright
#  notice appears in all copies and that both that copyright notice and the limited
#  warranty and restricted rights notice below appear in all supporting documentation.
#  AUTODESK PROVIDES THIS PROGRAM "AS IS" AND WITH ALL FAULTS. AUTODESK SPECIFICALLY
#  DISCLAIMS ANY IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR USE.
#  AUTODESK, INC. DOES NOT WARRANT THAT THE OPERATION OF THE PROGRAM WILL BE
#  UNINTERRUPTED OR ERROR FREE.
import os

import adsk.core
import adsk.fusion

from ... import config
from .logging import print_import_skip_message, info_log

app = adsk.core.Application.get()
ui = app.userInterface

# Configuration
SKIP_IMPORT_ON_DUPLICATES = config.SKIP_IMPORT_ON_DUPLICATES
UPLOAD_COUNT = 0


def import_project(source_folder, target_project, skip_import_on_duplicates):
    global SKIP_IMPORT_ON_DUPLICATES
    SKIP_IMPORT_ON_DUPLICATES = skip_import_on_duplicates

    if not os.path.exists(source_folder):
        ui.messageBox(f'Local Data Folder is missing:\n {source_folder}')

    project = get_data_project(target_project)
    root_data_folder = project.rootFolder

    import_local_folder(source_folder, root_data_folder)

    app.data.activeProject = project
    if not app.data.isDataPanelVisible:
        app.data.isDataPanelVisible = True
    app.data.refreshDataPanel()

    if UPLOAD_COUNT > 0:
        job_manager_command = ui.commandDefinitions.itemById('ShowJobManagerDlgCmd')
        job_manager_command.execute()
    info_log(f'Imported {UPLOAD_COUNT} Files to Project: {project.name}')


def import_local_folder(local_folder, data_folder):
    global UPLOAD_COUNT
    original_data_file_names = [df.name for df in data_folder.dataFiles.asArray()]

    for entry in os.scandir(local_folder):

        if entry.is_file():
            if entry.name.endswith('.f3d') or entry.name.endswith('.f3z'):
                if not (SKIP_IMPORT_ON_DUPLICATES and entry.name[:-4] in original_data_file_names):
                    info_log(f'Uploading: {data_folder.name}/{entry.name}')
                    data_folder.uploadFile(entry.path)
                    UPLOAD_COUNT += 1
                else:
                    print_import_skip_message(data_folder, entry, 'File already exists.')
            else:
                print_import_skip_message(data_folder, entry, 'Invalid file type.')

        if entry.is_dir():
            new_data_folder = get_data_folder(data_folder, entry.name)
            new_local_folder = os.path.join(local_folder, entry.name, '')
            import_local_folder(new_local_folder, new_data_folder)


def get_data_project(name: str) -> adsk.core.DataProject:
    for project in app.data.dataProjects.asArray():
        if project.name == name:
            return project

    new_project = app.data.dataProjects.add(name)
    return new_project


def get_data_folder(parent_folder: adsk.core.DataFolder, name: str) -> adsk.core.DataFolder:
    new_folder = parent_folder.dataFolders.itemByName(name)
    if new_folder:
        return new_folder

    new_folder = parent_folder.dataFolders.add(name)
    return new_folder

