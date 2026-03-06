import os

from core import types, file
from core.worker import filetree_builder


class SnapshotValidator:
    def __init__(self, direction: types.ViewDirection, bounds: tuple[str, str], subpath: str) -> None:
        """

        :param bounds: Structure of left and right bounds for timestamp filtering
        :param subpath: Sub-path inside tree for `by date` source tree type
        """
        self._direction = direction
        self._bounds = bounds
        self._subpath = subpath

    def __call__(self, path):
        # Validate timestamp
        path_parts = None
        if isinstance(path, str):
            path_parts = file.normalize_path_parts(path, self._direction.source)
        if isinstance(path, list):
            path_parts = path
        if path_parts is None:
            raise AttributeError("Incorrect argument type")
        timestamp = path_parts[0]

        if (len(self._bounds[0]) > 0) and (timestamp < self._bounds[0]):
            return False

        if (len(self._bounds[1]) > 0) and (timestamp > self._bounds[1]):
            return False

        # Validate sub-path
        if len(self._subpath) > 0:
            return file.join_path(path_parts[1:]).startswith(self._subpath)
        else:
            return True


class EmptyDirValidator:
    def __init__(self, files: list[tuple[str, str]]) -> None:
        self._files = files

    def __call__(self, directory: str):
        for f, _ in self._files:
            if f.startswith(directory):
                return False
        return True
