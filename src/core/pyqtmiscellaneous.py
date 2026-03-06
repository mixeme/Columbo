from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
from PyQt5.QtGui import QStandardItemModel

from core.types import OperationType


# Define signals for events
class Signals(QObject):
    load_finished = pyqtSignal()
    build_finished = pyqtSignal(OperationType, QStandardItemModel)
    delete_finished = pyqtSignal(OperationType)
    progress = pyqtSignal(str)


# Class is used to prevent error
# RuntimeError: wrapped C/C++ object of type FileTreeWorker has been deleted
class RunnableWrapper(QRunnable):
    @staticmethod
    def run_async(worker) -> None:
        QThreadPool.globalInstance().start(RunnableWrapper(worker))

    def __init__(self, runnable: QRunnable) -> None:
        super().__init__()
        self.runnable = runnable

    def run(self) -> None:
        self.runnable.run()
