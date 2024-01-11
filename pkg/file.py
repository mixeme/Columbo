import os.path
import time


def get_last_modified(path: str) -> str:
    time_val = os.path.getmtime(path)
    time_format = "%d.%m.%Y %H:%M:%S"  # Setup time format
    return time.strftime(time_format, time.localtime(time_val))


def get_snapshot(filename: str) -> str:
    sep = filename.rfind("_")
    dot = filename.rfind(".")

    if sep == -1:
        return ""
    if dot == -1:
        dot = len(filename)

    return filename[sep+1:dot]
