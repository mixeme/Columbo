import os
import os.path
import subprocess
import time


from core import types, snapshot


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


def is_empty_dir(directory: str, files: list[tuple[str, str]]) -> bool:
    for file, _ in files:
        if file.startswith(directory):
            return False
    return True


def split_path(path: str) -> list[str]:
    return path.split(os.sep)


def join_path(path_parts: list[str]) -> str:
    return os.sep.join(path_parts)


def resolve_relative_path(gathered_path: tuple[list[str], str], direction: types.ViewDirection):
    path_parts, timestamp = gathered_path

    if direction.source == direction.target:
        # Skip root
        source = join_path(path_parts[1:])
    else:
        if direction.by_date_to_unified():
            # Add timestamp, skip root
            copied = path_parts.copy()
            copied.insert(1, timestamp)
            source = join_path(copied[1:])

            # Add timestamp to filename
            path_parts[-1] = snapshot.set_timestamp(path_parts[-1], timestamp)
        else:
            # Skip root and snapshot folder
            source = join_path(path_parts[2:])

    target = join_path(path_parts[1:])
    return source, target


def normalize_path_parts(path: str, source_type: types.TreeType) -> list[str]:
    # Split path into components
    path_parts: list[str] = split_path(path)

    # Normalize paths
    # For "unified" source append a timestamp as the first path component
    if source_type == types.TreeType.UNIFIED:
        filename = path_parts[-1]
        path_parts.insert(0, snapshot.get_timestamp(filename))

    # Join back path
    return path_parts


def normalize_path(path: str, source_type: types.TreeType) -> str:
    # Join back path
    return join_path(normalize_path_parts(path, source_type))
