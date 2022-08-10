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

import adsk.cam
import adsk.core
import adsk.fusion

app = adsk.core.Application.get()
ui = app.userInterface


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
