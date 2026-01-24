import os

from PyQt5.QtCore import QRunnable

from core import file, pyqtmiscellaneous


class FileTreeLoader(QRunnable):
    signals = pyqtmiscellaneous.Signals()

    def __init__(self) -> None:
        # Declare fields
        self._root = None
        self.dirs = None
        self.files = None

        # Init lists
        self.reset()

    def reset(self) -> None:
        self.dirs = []
        self.files = []

    def set_root(self, root: str) -> None:
        self._root = root
        self.reset()

    def get_root(self) -> str:
        return self._root

    def load(self) -> None:
        self.reset()
        for dirpath, dirnames, filenames in os.walk(self._root):
            # Obtain absolute paths
            dirnames = [os.path.join(dirpath, i) for i in dirnames]
            filenames = [os.path.join(dirpath, i) for i in filenames]

            # Store relative paths to lists
            root_path = self._root + os.sep
            self.dirs.extend(map(lambda x: x.removeprefix(root_path), dirnames))
            self.files.extend(map(lambda x: (x.removeprefix(root_path), file.get_last_modified(x)), filenames))

        # Notify about load is finished
        FileTreeLoader.signals.load_finished.emit()

    def get_lists(self) -> (list[str], list[(str, int)]):
        return self.dirs, self.files

    def is_empty(self) -> bool:
        return (len(self.dirs) == 0) and (len(self.files) == 0)

    def run(self) -> None:
        self.load()
