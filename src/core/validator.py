import os

from core import snapshot
from core.snapshot import get_timestamp
from core.types import TreeType


class SnapshotValidator:
    def __init__(self, bounds: list[str], source_type: TreeType, sub_path: str) -> None:
        """

        :param bounds: Structure of left and right bounds for timestamp filtering
        :param source_type: Type of source tree
        :param sub_path: Sub-path inside tree for `by date` source tree type
        """
        self.bounds = bounds
        self.source_type = source_type
        self.sub_path = sub_path

    def validate(self, file_parts: list[str]):
        # Validate timestamp
        timestamp = self.timestamp_fun(file_parts)
        if (self.bounds[0] is not None) and (timestamp < self.bounds[0]):
            return False

    def validate_root(self, path_parts: list[str]) -> bool:
        """
        Function validates that path is within
        :param path_parts:
        :return:
        """
        if len(self.sub_path) == 0:
            return True
        else:
            return os.sep.join(path_parts[2:]).startswith(self.sub_path)
        if (self.bounds[1] is not None) and (timestamp > self.bounds[1]):
            return False

        # Validate sub-path
        if (len(self.sub_path) != 0) and (not os.sep.join(file_parts[1:]).startswith(self.sub_path)):
            return False

        return True

    def validate_timestamp(self, timestamp: str) -> bool:
        """
        :param timestamp: the timestamp of a snapshot
        :return: `True` if snapshot is within specified bounds; `False` - if not within specified bounds
        """
        if self.bounds[0] and timestamp < self.bounds[0]:
            return False

        if self.bounds[1] and timestamp > self.bounds[1]:
            return False

        return True

    def validate_file(self, path: str) -> bool:
        timestamp = None
        if self.source_type == TreeType.UNIFIED:
            timestamp = get_timestamp(os.path.basename(path))
        if self.source_type == TreeType.BY_DATE:
            timestamp = path.split(os.sep)[1]

        return self.validate_timestamp(timestamp)

    def test_file(self, root: str, file: str) -> bool:
        timestamp = None
        if self.source_type == TreeType.UNIFIED:
            timestamp = get_timestamp(file)
        if self.source_type == TreeType.BY_DATE:
            timestamp = root.split(os.sep)[1]

        return self.validate_timestamp(timestamp)


class Cleaner:
    def __init__(self, logger) -> None:
        self.logger = logger
