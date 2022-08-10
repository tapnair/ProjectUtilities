from .export_project import entry as export_project
from .import_folder import entry as import_folder
# from .stats import entry as stats

# Fusion will automatically call the start() and stop() functions.
commands = [
    export_project,
    import_folder,
    # stats,
]


# Assumes you defined a "start" function in each of your modules.
# The start function will be run when the add-in is started.
def start():
    for command in commands:
        command.start()


# Assumes you defined a "stop" function in each of your modules.
# The stop function will be run when the add-in is stopped.
def stop():
    for command in commands:
        command.stop()
