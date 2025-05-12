import os

from core import snapshot
from core.types import TreeType


class SnapshotValidator:
    def __init__(self, bounds: (str, str), source_type: TreeType, sub_path: str) -> None:
        """

        :param bounds: Structure of left and right bounds for timestamp filtering
        :param source_type: Type of source tree
        :param sub_path: Sub-path inside tree for `by date` source tree type
        """
        self.bounds = bounds
        self.sub_path = sub_path
        self.timestamp_fun = snapshot.get_timestamp_fun(source_type)

    def __call__(self, file_parts: list[str]):
        # Validate timestamp
        timestamp = self.timestamp_fun(file_parts)
        if (len(self.bounds[0]) > 0) and (timestamp < self.bounds[0]):
            return False

        if (len(self.bounds[1]) > 0) and (timestamp > self.bounds[1]):
            return False

        # Validate sub-path
        if (len(self.sub_path) > 0) and (not os.sep.join(file_parts[1:]).startswith(self.sub_path)):
            return False

        return True
