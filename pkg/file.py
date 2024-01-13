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


def clear_snapshots(root_path: str, test_snapshot_fun) -> None:
    for root, dirs, files in os.walk(root_path):
        for f in files:
            if test_snapshot_fun(root, f):
                try:
                    os.remove(os.path.join(root, f))
                except OSError:
                    print("Failed to delete", os.path.join(root, f))
                    pass
                #except FileNotFoundError:
                #    pass
