#  Copyright 2022 by Autodesk, Inc.
#  Permission to use, copy, modify, and distribute this software in object code form
#  for any purpose and without fee is hereby granted, provided that the above copyright
#  notice appears in all copies and that both that copyright notice and the limited
#  warranty and restricted rights notice below appear in all supporting documentation.
#
#  AUTODESK PROVIDES THIS PROGRAM "AS IS" AND WITH ALL FAULTS. AUTODESK SPECIFICALLY
#  DISCLAIMS ANY IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR USE.
#  AUTODESK, INC. DOES NOT WARRANT THAT THE OPERATION OF THE PROGRAM WILL BE
#  UNINTERRUPTED OR ERROR FREE.
import os

import adsk.cam
import adsk.core
import adsk.fusion
import traceback

from ... import config

# Configuration
PROJECT_NAME = config.PROJECT_NAME
DO_EXPORT = config.DO_EXPORT
SKIP_IMPORT_ON_DUPLICATES = config.SKIP_IMPORT_ON_DUPLICATES
SKIP_EXPORT_ON_PARENTS = config.SKIP_EXPORT_ON_PARENTS
SKIP_EXPORT_ON_CHILDREN = config.SKIP_EXPORT_ON_CHILDREN
SKIP_EXPORT_ON_DUPLICATES = config.SKIP_EXPORT_ON_DUPLICATES
LOCAL_FUSION_FOLDER = config.LOCAL_FUSION_FOLDER
AUTO_SHOW_TEXT_COMMAND_PALETTE = config.AUTO_SHOW_TEXT_COMMAND_PALETTE

# Globals
HANDLERS = []
OPEN_DOCS = {}
CLOSE_EVENT_ID = 'closeEventId'
CLOSE_EVENT: adsk.core.CustomEvent = None
EXPORT_DONE = False
UPLOAD_COUNT = 0
ROOT_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    LOCAL_FUSION_FOLDER, PROJECT_NAME, ''
)

app = adsk.core.Application.get()
ui = app.userInterface


def run(context):
    try:
        if AUTO_SHOW_TEXT_COMMAND_PALETTE:
            textPalette = ui.palettes.itemById('TextCommands')
            if not textPalette.isVisible:
                textPalette.isVisible = True

        if DO_EXPORT:
            export_project()
        else:
            import_project()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            adsk.terminate()


def stop(context):
    try:
        if len(HANDLERS) > 0:
            CLOSE_EVENT.remove(HANDLERS[0])
            app.unregisterCustomEvent(CLOSE_EVENT_ID)
        info_log('Script Complete')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def import_project():
    if not os.path.exists(ROOT_FOLDER):
        ui.messageBox(f'Local Data Folder is missing:\n {ROOT_FOLDER}')

    project = get_data_project(PROJECT_NAME)
    root_data_folder = project.rootFolder

    import_local_folder(ROOT_FOLDER, root_data_folder)

    app.data.activeProject = project
    if not app.data.isDataPanelVisible:
        app.data.isDataPanelVisible = True
    app.data.refreshDataPanel()

    if UPLOAD_COUNT > 0:
        job_manager_command = ui.commandDefinitions.itemById('ShowJobManagerDlgCmd')
        job_manager_command.execute()
    info_log(f'Imported {UPLOAD_COUNT} Files to Project: {project.name}')
    adsk.terminate()


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


def export_project():
    global CLOSE_EVENT
    global EXPORT_DONE

    CLOSE_EVENT = app.registerCustomEvent(CLOSE_EVENT_ID)
    onCloseEvent = CloseEventHandler()
    CLOSE_EVENT.add(onCloseEvent)
    HANDLERS.append(onCloseEvent)

    project = app.data.activeProject
    root_data_folder = project.rootFolder

    confirm_msg = f'Export {project.name}?\nSee results and skipped files in "Text Commands" below.'
    dialog_result = ui.messageBox(
        confirm_msg,
        'Project Data Exporter',
        adsk.core.MessageBoxButtonTypes.OKCancelButtonType,
        adsk.core.MessageBoxIconTypes.QuestionIconType
    )

    if dialog_result == adsk.core.DialogResults.DialogOK:
        export_data_folder(root_data_folder, ROOT_FOLDER)

    if len(OPEN_DOCS.keys()) > 0:
        adsk.autoTerminate(False)
        EXPORT_DONE = True
        return

    adsk.terminate()


def export_data_folder(data_folder: adsk.core.DataFolder, local_folder: str):
    for folder in data_folder.dataFolders:
        new_local_folder = os.path.join(local_folder, folder.name, "")
        if not os.path.exists(new_local_folder):
            os.makedirs(new_local_folder)

        export_data_folder(folder, new_local_folder)

    for data_file in data_folder.dataFiles:
        if data_file.fileExtension == "f3d":

            if SKIP_EXPORT_ON_CHILDREN and data_file.hasChildReferences:
                print_export_skip_message(data_file, 'Has child references.  Export an f3z.')

            elif SKIP_EXPORT_ON_PARENTS and data_file.hasParentReferences:
                print_export_skip_message(data_file, 'Has parent references:', True)

            else:
                export_data_file(data_file, local_folder)

        elif data_file.fileExtension == "f2d":
            print_export_skip_message(data_file, 'Manually Export Drawings')

        else:
            print_export_skip_message(data_file, f'Non-Fusion file type: {data_file.fileExtension}')


def export_data_file(data_file, local_folder):
    try:
        local_file_name = data_file.name + '.f3d'
        local_full_path = os.path.join(local_folder, local_file_name)

        is_duplicate = duplicate_check(local_full_path)
        if SKIP_EXPORT_ON_DUPLICATES and is_duplicate:
            print_export_skip_message(data_file, 'File already exists')
            return True

        document = app.documents.open(data_file, True)
        if document is not None:
            document.activate()
            export_document(document, local_full_path)

            OPEN_DOCS[local_full_path] = document
            app.fireCustomEvent(CLOSE_EVENT_ID, local_full_path)
            return True

        print_export_skip_message(data_file, 'Document failed to open')
        return False

    except:
        print_export_skip_message(data_file, 'Script Error')


def export_document(document: adsk.core.Document, local_full_path: str):
    design: adsk.fusion.Design = document.products.itemByProductType('DesignProductType')
    export_mgr = design.exportManager
    export_options = export_mgr.createFusionArchiveExportOptions(local_full_path)
    export_mgr.execute(export_options)


def duplicate_check(local_full_path):
    if os.path.exists(local_full_path):
        if not SKIP_EXPORT_ON_DUPLICATES:
            os.remove(local_full_path)
        return True
    return False


def print_export_skip_message(data_file: adsk.core.DataFile, message: str, parents=False):
    info_log()
    info_log(f'Skipped: {data_file.parentFolder.name}/{data_file.name}')
    info_log(f' => {message}')
    if parents:
        for reference in data_file.parentReferences:
            info_log(f'    * {reference.parentFolder.name}/{reference.name}')
    info_log()


def print_import_skip_message(data_folder: adsk.core.DataFolder, entry, message: str):
    info_log()
    info_log(f'Skipped: {data_folder.name}/{entry.name}')
    info_log(f' => {message}')
    info_log()


def info_log(message=' '):
    app.log(message, adsk.core.LogLevels.InfoLogLevel, adsk.core.LogTypes.ConsoleLogType)


class CloseEventHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            local_full_path = args.additionalInfo
            document: adsk.core.Document = OPEN_DOCS[local_full_path]
            success = document.close(False)

            if success:
                OPEN_DOCS.pop(local_full_path)

            if EXPORT_DONE and len(OPEN_DOCS.keys()) == 0:
                adsk.terminate()
        except:
            msg = 'Failed:\n{}'.format(traceback.format_exc())
            app.log(msg, adsk.core.LogLevels.ErrorLogLevel, adsk.core.LogTypes.ConsoleLogType)
