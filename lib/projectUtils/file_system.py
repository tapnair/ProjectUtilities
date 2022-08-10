import adsk.core

app = adsk.core.Application.get()
ui = app.userInterface


# Create file browser dialog
def get_file_dialog():
    file_dialog = ui.createFileDialog()
    file_dialog.filter = ".zip files (*.zip);;All files (*.*)"
    file_dialog.isMultiSelectEnabled = False
    file_dialog.title = 'Select an archived project zip file'

    dialog_results = file_dialog.showOpen()
    if dialog_results == adsk.core.DialogResults.DialogOK:
        if len(file_dialog.filenames) == 1:
            return file_dialog.filename

    return ''


# Create folder browser dialog
def get_folder_dialog():
    folder_dialog = ui.createFolderDialog()
    folder_dialog.filter = ".zip files (*.zip);;All files (*.*)"
    folder_dialog.isMultiSelectEnabled = False
    folder_dialog.title = 'Select an archived project zip file'

    dialog_results = folder_dialog.showDialog()
    if dialog_results == adsk.core.DialogResults.DialogOK:
        if len(folder_dialog.folder) > 0:
            return folder_dialog.folder

    return ''

