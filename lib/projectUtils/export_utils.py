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
import traceback

import adsk.cam
import adsk.core
import adsk.fusion

from ... import config

from .logging import print_export_skip_message
app = adsk.core.Application.get()
ui = app.userInterface


# Configuration
SKIP_EXPORT_ON_PARENTS = True
SKIP_EXPORT_ON_CHILDREN = config.SKIP_EXPORT_ON_CHILDREN
SKIP_EXPORT_ON_DUPLICATES = True


# Globals
HANDLERS = []
OPEN_DOCS = {}
CLOSE_EVENT_ID = 'closeEventId'
CLOSE_EVENT: adsk.core.CustomEvent = None


def clean_up_export_utils():
    if len(HANDLERS) > 0:
        CLOSE_EVENT.remove(HANDLERS[0])
        app.unregisterCustomEvent(CLOSE_EVENT_ID)


def export_project(target_folder, skip_export_on_parents, skip_export_on_duplicates):
    global SKIP_EXPORT_ON_PARENTS
    global SKIP_EXPORT_ON_DUPLICATES
    SKIP_EXPORT_ON_PARENTS = skip_export_on_parents
    SKIP_EXPORT_ON_DUPLICATES = skip_export_on_duplicates

    global CLOSE_EVENT
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
        export_data_folder(root_data_folder, target_folder)


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

        except:
            msg = 'Failed:\n{}'.format(traceback.format_exc())
            app.log(msg, adsk.core.LogLevels.ErrorLogLevel, adsk.core.LogTypes.ConsoleLogType)



