import os
import os.path
import subprocess
import time


# Global constant
time_format = "%d.%m.%Y %H:%M:%S"  # Setup time format


def open_file(path: str) -> None:
    try:
        os.startfile(path)                  # Windows version
    except AttributeError:
        subprocess.call(['open', path])     # Linux version


def get_last_modified(path: str) -> str:
    time_val = os.path.getmtime(path)
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
