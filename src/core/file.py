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


def is_empty_dir(dir: str, files: list[tuple[str, str]]) -> bool:
    for file, _ in files:
        if file.startswith(dir):
            return False
    return True


def list_dir(root: str) -> (list[str], list[(str, int)]):
    dirs = []
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Obtain absolute paths
        dirnames = [os.path.join(dirpath, i) for i in dirnames]
        filenames = [os.path.join(dirpath, i) for i in filenames]

        # Store items to lists
        dirs.extend(map(lambda x: x.removeprefix(root + os.sep), dirnames))
        files.extend(map(lambda x: (x.removeprefix(root + os.sep), get_last_modified(x)), filenames))

    return dirs, files
