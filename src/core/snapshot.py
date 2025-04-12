import os

from core.types import TreeType


class SnapshotTester:
    def __init__(self, bounds: list[str], source_type: TreeType, sub_path: str) -> None:
        """

        :param bounds: Structure of left and right bounds for snapshot filter
        :param source_type: Type of source tree
        :param sub_path: Sub-path inside tree for `by date` source tree type
        """
        self.bounds = bounds
        self.source_type = source_type
        self.sub_path = sub_path

    def test_root(self, path_parts: list[str]) -> bool:
        if len(self.sub_path) == 0:
            return True
        else:
            return os.sep.join(path_parts[2:]).startswith(self.sub_path)

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

    def test_file(self, root: str, file: str) -> bool:
        snapshot = None
        if self.source_type == TreeType.UNIFIED:
            snapshot = get_snapshot(file)
        if self.source_type == TreeType.BY_DATE:
            snapshot = root.split(os.sep)[1]

        return self.test_snapshot(snapshot)


class Cleaner:
    def __init__(self, logger) -> None:
        self.logger = logger


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
