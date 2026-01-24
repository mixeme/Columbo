import os

from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable
from PyQt5.QtGui import QStandardItemModel

from core import file, node, snapshot, filetree_loader
from core.data_model import FileSortFilterProxyModel
from core.pyqtmiscellaneous import Signals
from core.types import TreeType, OperationType


class FileTreeWBuilder(QRunnable):
    columns = ["Name", "Last modified", "Snapshot"]
    signals = Signals()

    def __init__(self, loader: filetree_loader.FileTreeLoader):
        super().__init__()
        # Store file lists loader
        self._loader = loader

        # Declare fields
        self._direction = None
        self._operation = None
        self._validator = None
        self._root_node = None
        self._sort_rows = None
        self._data_model = None

    def set_options(self, direction, operation) -> None:
        self._direction = direction
        self._operation = operation

    def set_validator(self, validator) -> None:
        self._validator = validator

    def get_abs(self, path: str) -> str:
        return os.path.join(self._loader.get_root(), path)

    def init_root(self) -> None:
        # Create root row
        root_row = node.create_folder_node(self._loader.get_root())

        # Create data model
        model = QStandardItemModel()
        model.invisibleRootItem().appendRow(root_row)
        model.setHorizontalHeaderLabels(FileTreeWBuilder.columns)

        # Create proxy data model for sorting customization
        proxy_model = FileSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        self._sort_rows = lambda: proxy_model.sort(0, QtCore.Qt.AscendingOrder)
        self._data_model = proxy_model

        # Store 1st column of the root row
        self._root_node = root_row[0]

    def list_dir(self):
        if self.loader.is_empty():
            self.loader.load()

    def drop_lists(self) -> None:
        self.loader.reset()

    def create_tree(self, routine):
        # Create tree root
        self.init_root()

        # List directory
        self.list_dir()

        # Create tree nodes
        routine()

    def tree_files(self):
        timestamp_fun = snapshot.get_timestamp_fun(self.direction[0])

        self_files = self.loader.files

        # Split path into components
        files_parts = [(path.split(os.sep), date) for path, date in self_files]

        # Normalize paths to "by date" format: append a timestamp as the first path component
        if self.direction[0] == TreeType.UNIFIED:
            for path_parts, _ in files_parts:
                path_parts.insert(0, timestamp_fun(path_parts))

        # Define starting component of a path
        # "by date" view starts with a timestamp component; "unified" view skips a timestamp component
        if self.direction[1] == TreeType.BY_DATE:
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
                node.add_file_node(current, self.direction, filename, last_modified, timestamp)

    def tree_empty_dirs(self):
        self_dirs = self.loader.dirs
        self_files = self.loader.files

        for d in self_dirs:
            if file.is_empty_dir(d, self_files):
                # Find corresponding node for the root
                node.descend_by_path(self.root_node, d.split(os.sep))

    def clear_files(self):
        self_files = self.loader.files

        # Split path into components
        files_parts = [(path.split(os.sep), date) for path, date in self_files]

        for file_parts, _ in files_parts:
            if self.validator(file_parts):
                path = os.path.join(self.root_path, os.sep.join(file_parts))
                try:
                    os.remove(path)
                    self.signals.progress.emit("Deleted " + path)
                except OSError:
                    self.signals.progress.emit("Failed to delete " + path)

        self.signals.operation = self.operation
        self.signals.clear_finished.emit(self.operation)

    def clear_empty_dirs(self):
        dirs, files = self.loader.get_lists()

        for d in dirs:
            if file.is_empty_dir(d, files):
                path = self.get_abs(d)
                try:
                    os.removedirs(path)
                    self.signals.progress.emit("Deleted " + path)
                except OSError:
                    self.signals.progress.emit("Failed to delete" + path)

        self.signals.operation = self.operation
        self.signals.clear_finished.emit(self.operation)

    def run(self) -> None:
        if self.loader.is_empty():
            self.filetree_load_action()

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
            self.list_dir()     # List directory
            routine_clear()     # Create tree nodes
