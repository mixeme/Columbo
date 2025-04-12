import os
import os.path
import subprocess
import time


def open_file(path: str) -> None:
    try:
        os.startfile(path)                  # Windows version
    except AttributeError:
        subprocess.call(['open', path])     # Linux version


def get_last_modified(path: str) -> str:
    time_val = os.path.getmtime(path)
    time_format = "%d.%m.%Y %H:%M:%S"  # Setup time format
    return time.strftime(time_format, time.localtime(time_val))


def get_file_extension(filename: str) -> str:
    dot = filename.rfind(".")
    if dot == -1:
        return ""
    else:
        return filename[dot+1:]


def remove_empty_dirs(path: str) -> None:
    for root, dirs, files in os.walk(path):
        if len(dirs) == 0 and len(files) == 0:
            os.removedirs(root)


def remove_files(path: str, predicate_fun) -> None:
    for root, dirs, files in os.walk(path):
        for f in files:
            if predicate_fun(root, f):
                try:
                    os.remove(os.path.join(root, f))
                except OSError:
                    pass
