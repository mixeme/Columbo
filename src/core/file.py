import os.path
import time
from core.types import TreeType


def get_last_modified(path: str) -> str:
    time_val = os.path.getmtime(path)
    time_format = "%d.%m.%Y %H:%M:%S"  # Setup time format
    return time.strftime(time_format, time.localtime(time_val))


def get_snapshot(filename: str) -> str:
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


def clear_snapshots(root_path: str, test_snapshot_fun) -> None:
    for root, dirs, files in os.walk(root_path):
        for f in files:
            if test_snapshot_fun(root, f):
                try:
                    os.remove(os.path.join(root, f))
                except OSError:
                    pass


class SnapshotTester:
    def __init__(self, bounds: list[str], source_type: TreeType) -> None:
        self.bounds = bounds
        self.type = source_type

    def test_snapshot(self, snapshot: str) -> bool:
        """
        :param snapshot: the timestamp of a snapshot
        :return: `True` if snapshot is within specified bounds; `False` - if not within specified bounds
        """
        if self.bounds[0] and snapshot < self.bounds[0]:
            return False

        if self.bounds[1] and snapshot > self.bounds[1]:
            return False

        return True

    def test_file(self, root, file) -> bool:
        snapshot = None
        if self.type == TreeType.UNIFIED:
            snapshot = get_snapshot(file)
        if self.type == TreeType.BY_DATE:
            snapshot = root.split(os.sep)[1]

        return self.test_snapshot(snapshot)
