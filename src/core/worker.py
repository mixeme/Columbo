import os

from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
from PyQt5.QtGui import QStandardItemModel

from core import file, node, snapshot
from core.tree import FileSortFilterProxyModel
from core.types import TreeType, OperationType


# Define signals for events
class Signals(QObject):
    build_finished = pyqtSignal(OperationType, QStandardItemModel)
    clear_finished = pyqtSignal(OperationType)
    progress = pyqtSignal(str)


class FileTreeWorker(QRunnable):
    columns = ["Name", "Last modified", "Snapshot"]
    signals = Signals()

    def __init__(self, root_path: str):
        """

        :param root_path: A path for history storage
        """
        super().__init__()
        # Store input values
        self.root_path = root_path

        # Declare fields
        self.checked_options = None
        self.operation = None
        self.root_node = None
        self.sort_rows = None
        self.validator = None
        self.data_model = None
        self.dirs = []
        self.files = []

    def init_root(self) -> None:
        # Create root row
        root_row = node.create_folder_node(self.root_path)

        # Create data model
        model = QStandardItemModel()
        model.invisibleRootItem().appendRow(root_row)
        model.setHorizontalHeaderLabels(FileTreeWorker.columns)

        # Create proxy data model for sorting customization
        proxy_model = FileSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        self.sort_rows = lambda: proxy_model.sort(0, QtCore.Qt.AscendingOrder)
        self.data_model = proxy_model

        # Store 1st column of the root row
        self.root_node = root_row[0]

    def create_tree(self, routine):
        # Create tree root
        self.init_root()

        # List directory
        if (len(self.dirs) == 0) and (len(self.files) == 0):
            self.dirs, self.files = file.list_dir(self.root_path)

        # Create tree nodes
        routine()

    def tree_files(self):
        timestamp_fun = snapshot.get_timestamp_fun(self.checked_options[0])

        # Split path into components
        files_parts = [(path.split(os.sep), date) for path, date in self.files]

        # Normalize paths to "by date" format: append a timestamp as the first path component
        if self.checked_options[0] == TreeType.UNIFIED:
            for path_parts, _ in files_parts:
                path_parts.insert(0, timestamp_fun(path_parts))

        # Define starting component of a path
        # "by date" view starts with a timestamp component; "unified" view skips a timestamp component
        if self.checked_options[1] == TreeType.BY_DATE:
            start_pos = 0
        else:
            start_pos = 1

        for file_parts, last_modified in files_parts:
            if self.validator(file_parts):
                # Find corresponding node for the root
                current = node.descend_by_path(self.root_node, file_parts[start_pos:-1])

                # File name
                filename = file_parts[-1]

                # Get timestamp
                timestamp = timestamp_fun(file_parts)

                # Add file node
                node.add_file_node(current, self.checked_options, filename, last_modified, timestamp)

    def tree_empty_dirs(self):
        for d in self.dirs:
            if file.is_empty_dir(d, self.files):
                # Find corresponding node for the root
                node.descend_by_path(self.root_node, d.split(os.sep))

    def clear_files(self):
        # Split path into components
        files_parts = [(path.split(os.sep), date) for path, date in self.files]

        for file_parts, _ in files_parts:
            if self.validator(file_parts):
                path = os.path.join(self.root_path, os.sep.join(file_parts))
                try:
                    os.remove(path)
                    self.signals.progress.emit("Deleted " + path)
                except OSError:
                    self.signals.progress.emit("Failed to delete " + path)
        self.signals.clear_finished.emit(self.operation)

    def clear_empty_dirs(self):
        for d in self.dirs:
            if file.is_empty_dir(d, self.files):
                path = os.path.join(self.root_path, d)
                try:
                    os.removedirs(path)
                    self.signals.progress.emit("Deleted " + path)
                except OSError:
                    self.signals.progress.emit("Failed to delete" + path)
        self.signals.clear_finished.emit(self.operation)

    def run(self) -> None:
        # Define routine function independence of operation
        routine_tree = None
        routine_clear = None
        if (self.operation == OperationType.FILE_TREE) or (self.operation == OperationType.FILTERED_TREE):
            routine_tree = self.tree_files
        if self.operation == OperationType.EMPTY_DIRS:
            routine_tree = self.tree_empty_dirs

        if self.operation == OperationType.CLEAR_SNAPSHOTS:
            routine_clear = self.clear_files
        if self.operation == OperationType.CLEAR_EMPTY_DIRS:
            routine_clear = self.clear_empty_dirs

        if routine_tree is not None:
            # Finishing tree build
            self.create_tree(routine_tree)   # Build tree
            self.sort_rows()            # Sort nodes

            # Signal object should possess the sending data
            self.signals.operation = self.operation
            self.signals.model = self.data_model

            # Signal tree update
            self.signals.build_finished.emit(self.operation, self.data_model)

        if routine_clear is not None:
            # List directory
            if (len(self.dirs) == 0) and (len(self.files) == 0):
                self.dirs, self.files = file.list_dir(self.root_path)

            # Create tree nodes
            routine_clear()


# Class is used to prevent error
# RuntimeError: wrapped C/C++ object of type FileTreeWorker has been deleted
class WorkerWrapper(QRunnable):
    def __init__(self, worker: FileTreeWorker) -> None:
        super().__init__()
        self.worker = worker

    def run(self) -> None:
        self.worker.run()
