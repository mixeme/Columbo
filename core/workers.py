import os

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal


class Signals(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal()


class ClearEmptyDirsWorker(QRunnable):
    signals = Signals()

    def __init__(self, root_path: str):
        super().__init__()
        self.root_path = root_path

    def run(self) -> None:
        for root, dirs, files in os.walk(self.root_path):
            if len(dirs) == 0 and len(files) == 0:
                try:
                    os.removedirs(root)
                    self.signals.progress.emit("Delete" + root)
                except OSError:
                    self.signals.progress.emit("Failed to delete" + root)
        self.signals.finished.emit()


class ClearSnapshotWorker(QRunnable):
    signals = Signals()

    def __init__(self, root_path: str, test_snapshot):
        super().__init__()
        self.root_path = root_path
        self.test_snapshot = test_snapshot

    def run(self) -> None:
        for root, dirs, files in os.walk(self.root_path):
            for f in files:
                if self.test_snapshot(root, f):
                    path = os.path.join(root, f)
                    try:
                        os.remove(path)
                        self.signals.progress.emit("Delete" + path)
                    except OSError:
                        self.signals.progress.emit("Failed to delete" + path)
        self.signals.finished.emit()
