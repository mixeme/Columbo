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
                os.removedirs(root)
                self.signals.progress.emit("Delete" + root)
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
                    try:
                        os.remove(os.path.join(root, f))
                        self.signals.progress.emit("Delete" + os.path.join(root, f))
                    except OSError:
                        self.signals.progress.emit("Failed to delete" + os.path.join(root, f))
                        pass
        self.signals.finished.emit()
