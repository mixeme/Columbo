import os
import os.path
import subprocess
import time
from core.types import TreeType


def get_last_modified(path: str) -> str:
    time_val = os.path.getmtime(path)
    time_format = "%d.%m.%Y %H:%M:%S"  # Setup time format
    return time.strftime(time_format, time.localtime(time_val))


def get_snapshot(filename: str) -> str:
    """
    :param filename: Name of a file that contains a timestamp as a suffix starting with "_"
    :return: Timestamp designating snapshot
    """
    dot = filename.rfind(".")
    if dot == -1:
        dot = len(filename)

    sep = filename.rfind("_", 0, dot)
    if sep == -1:
        return ""

    return filename[sep+1:dot]


def get_extension(filename: str) -> str:
    dot = filename.rfind(".")
    if dot == -1:
        return ""
    else:
        return filename[dot+1:]


def clear_empty_dirs(root_path: str) -> None:
    for root, dirs, files in os.walk(root_path):
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
