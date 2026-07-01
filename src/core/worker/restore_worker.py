import os
import shutil

from PyQt5.QtCore import QRunnable

from core import types, file, pyqtmiscellaneous


class RestoreWorker(QRunnable):
    signals = pyqtmiscellaneous.Signals()

    def __init__(self):
        super().__init__()
        self._operation = None
        self._direction = None
        self._source = None
        self._target = None

    def set_details(self,operation: types.OperationType, direction: types.ViewDirection, source, target):
        self._operation = operation
        self._direction = direction
        self._source = source
        self._target = target

    def restore_file(self):
        if len(self._target) > 0:
            shutil.copy2(self._source, self._target)
            self.signals.progress.emit("Restored " + self._source)

    def restore_dir(self):
        for source_path in self._source:
            parts_parts, _ = source_path
            source_rel, target_rel = file.resolve_relative_path(source_path, self._direction)
            source = os.path.join(parts_parts[0], source_rel)
            target = os.path.join(self._target, target_rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(source, target)
            self.signals.progress.emit("Restored " + source)

    def run(self) -> None:
        if self._operation == types.OperationType.RESTORE_FILE:
            self.restore_file()
        if self._operation == types.OperationType.RESTORE_DIR:
            self.restore_dir()

        self.signals.operation = self._operation
        self.signals.restoration_finished.emit(self._operation)
