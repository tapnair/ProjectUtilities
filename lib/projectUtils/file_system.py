
app = adsk.core.Application.get()
ui = app.userInterface


def get_file_dialog():
    # Create file browser dialog box
    file_dialog = ui.createFileDialog()
    file_dialog.filter = ".DXF files (*.dxf);;All files (*.*)"
    file_dialog.isMultiSelectEnabled = True
    file_dialog.title = 'Select dxf files to import'
    dialog_results = file_dialog.showOpen()
    if dialog_results == adsk.core.DialogResults.DialogOK:
        self.file_names = file_dialog.filenames
    else:
        command.isAutoExecute = True
        return
