import os

from PyQt5.QtCore import QRunnable

from core import pyqtmiscellaneous, types
from core.worker.filetree_loader import FileTreeLoader
from core.validator import EmptyDirValidator


class FileTreeDeleter(QRunnable):
    signals = pyqtmiscellaneous.Signals()

    def __init__(self, loader: FileTreeLoader):
        super().__init__()
        # Store file lists loader
        self._loader = loader

        # Declare fields
        self._direction = None
        self._operation = None
        self._validator = None

    def set_direction(self, direction: types.ViewDirection) -> None:
        self._direction = direction

    def set_operation(self, operation: types.OperationType) -> None:
        self._operation = operation

    def set_validator(self, validator) -> None:
        self._validator = validator

    def get_abs(self, path: str) -> str:
        return os.path.join(self._loader.get_root(), path)

    def delete_routine(self, items, validator):
        for i in items:
            if validator(i):
                path: str = self.get_abs(i)
                try:
                    if os.path.isfile(path) or os.path.isdir(path):
                        if os.path.isfile(path):
                            os.remove(path)
                        else:
                            os.removedirs(path)
                    else:
                        raise OSError("Unknown object associated with path")
                    self.signals.progress.emit("Deleted " + path)
                except OSError:
                    self.signals.progress.emit("Failed to delete " + path)

        self.signals.operation = self._operation
        self.signals.delete_finished.emit(self._operation)

    def delete_files(self):
        files = self._loader.get_normalized_paths(self._direction.source)
        paths = [path for path, _ in files]
        self.delete_routine(paths, self._validator)

    def delete_empty_dirs(self):
        dirs, files = self._loader.get_lists()
        validator = EmptyDirValidator(files)
        self.delete_routine(dirs, validator)

    def run(self) -> None:
        # Check loader status
        if self._loader.is_empty():
            raise AttributeError()

        # Perform deletion
        if self._operation == types.OperationType.DELETE_SNAPSHOTS:
            self.delete_files()
        if self._operation == types.OperationType.DELETE_EMPTY_DIRS:
            self.delete_empty_dirs()

        # Reset load status after deletion
        self._loader.reset()
