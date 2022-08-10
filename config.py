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

DEBUG = True

ADDIN_NAME = os.path.basename(os.path.dirname(__file__))
COMPANY_NAME = "Autodesk"

# Name for a directory in user home to store data
user_dir_name = f'{ADDIN_NAME}'

# Design Workspace
design_workspace = 'FusionSolidEnvironment'

# Utilities Tab
utilities_tab_id = 'ToolsTab'
utilities_tab_name = 'UTILITIES'

project_utilities_panel_name = 'Projects'
project_utilities_panel_id = f'{ADDIN_NAME}_project_utilities_panel'
project_utilities_panel_after = 'SolidScriptsAddinsPanel'


# *************************** Default Options ****************************

# When set True, it will skip import when file already exists in project
SKIP_IMPORT_ON_DUPLICATES = True

# When set True, it will skip exporting files with parent references
SKIP_EXPORT_ON_PARENTS = True

# When set True, it will skip exporting files with child references
SKIP_EXPORT_ON_CHILDREN = True

# When set True, will skip export when file already exists in folder
SKIP_EXPORT_ON_DUPLICATES = True

# When set True, will show text command palettes automatically
# Particularly useful when running export command
# For mass distribution should probably be set False
AUTO_SHOW_TEXT_COMMANDS = False
# ***********************************************************************
