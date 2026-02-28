import os

from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable
from PyQt5.QtGui import QStandardItemModel

from core import file, node, types
from core.worker import filetree_loader
from core.data_model import FileSortFilterProxyModel
from core.pyqtmiscellaneous import Signals
from core.types import TreeType, OperationType


# Define starting component of a path
# "by date" view starts with a timestamp component; "unified" view skips a timestamp component
def get_start_pos(target: types.TreeType) -> int:
    return 0 if target == TreeType.BY_DATE else 1


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

    def set_direction(self, direction: types.ViewDirection) -> None:
        self._direction = direction

    def set_operation(self, operation: types.OperationType) -> None:
        self._operation = operation

    def set_validator(self, validator) -> None:
        self._validator = validator

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

    def create_tree(self, routine):
        # Create tree root
        self.init_root()

        # List directory
        if self._loader.is_empty():
            self._loader.load()

        # Create tree nodes
        routine()

    def tree_files(self):
        # Get normalized paths
        files_parts = self._loader.get_normalized_paths_parts(self._direction.source)

        # Define starting component of a path
        # "by date" view starts with a timestamp component; "unified" view skips a timestamp component
        start_pos = get_start_pos(self._direction.target)

        for file_parts, last_modified in files_parts:
            if self._validator(file_parts):
                # Find corresponding node for the root
                current = node.descend_by_path(self._root_node, file_parts[start_pos:-1])

                # File name
                filename = file_parts[-1]

                # Get timestamp
                timestamp = file_parts[0]

                # Add file node
                node.add_file_node(current, self._direction, filename, last_modified, timestamp)

    def tree_dirs(self):
        dirs, files = self._loader.get_lists()

        for d in dirs:
            if self._validator(d):
                # Find corresponding node for the root
                node.descend_by_path(self._root_node, d.split(os.sep))

    def run(self) -> None:
        # Build tree
        if (self._operation == OperationType.FULL_TREE) or (self._operation == OperationType.FILTERED_TREE):
            self.create_tree(self.tree_files)
        if self._operation == OperationType.EMPTY_DIRS:
            self.create_tree(self.tree_dirs)

        # Sort nodes
        self._sort_rows()

        # Signal object should possess the sending data
        self.signals.operation = self._operation
        self.signals.model = self._data_model

        # Signal tree update
        self.signals.build_finished.emit(self._operation, self._data_model)
