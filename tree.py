import os
from enum import Enum

from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable, pyqtSignal, QObject
from PyQt5.QtGui import QStandardItemModel

from pkg import file, nodes


class TreeType(Enum):
    UNIFIED = 0
    BY_DATE = 1


class OperationType(Enum):
    FILE_TREE = 0
    FILTERED_TREE = 1
    EMPTY_DIRS = 2


class FileSortFilterProxyModel(QtCore.QSortFilterProxyModel):
    def lessThan(self, left, right):
        # Retrieve names
        left_name = left.data()
        right_name = right.data()
        # Retrieve dates
        left_date = left.siblingAtColumn(1).data()
        right_date = right.siblingAtColumn(1).data()
        # Retrieve snapshots
        left_snapshot = left.siblingAtColumn(2).data()
        right_snapshot = right.siblingAtColumn(2).data()

        # Left & right items are folders
        if (left_date == "Folder") and (right_date == "Folder"):
            return left_name < right_name   # Compare their names

        # Left - folder, right - file
        if left_date == "Folder":
            return True                     # Folder less than file

        # Right - folder, left - file
        if right_date == "Folder":
            return False                    # Folder not less than file

        # Left & right items are files with the same name
        # This is case "by date -> unified"
        if left_name == right_name:
            return left_snapshot < right_snapshot   # Compare timestamp of snapshots

        # All other cases
        return left_name < right_name


class Signals(QObject):
    finished = pyqtSignal(OperationType, QStandardItemModel)


class FileTreeWorker(QRunnable):
    columns = ["Name", "Last modified", "Snapshot"]
    signals = Signals()

    def __init__(self, root_path, checked_options, operation: OperationType):
        super().__init__()
        # Store input values
        self.root_path = root_path
        self.checked = checked_options
        self.operation = operation

        # Declare fields
        self.root_node = None
        self.sort_rows = None
        self.filter = False
        self.from_snapshot = None
        self.to_snapshot = None
        self.model = None

    def set_filter(self, from_snapshot: str, to_snapshot: str):
        self.filter = True
        self.from_snapshot = from_snapshot
        self.to_snapshot = to_snapshot

    def init_root(self) -> None:
        # Create root node
        root_node = nodes.create_folder(self.root_path)

        # Create data model
        model = QStandardItemModel()
        model.invisibleRootItem().appendRow(root_node)
        model.setHorizontalHeaderLabels(FileTreeWorker.columns)

        # Create proxy data model for sorting customisation
        proxy_model = FileSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        self.sort_rows = lambda: proxy_model.sort(0, QtCore.Qt.AscendingOrder)
        self.model = proxy_model

        # Store 1st column of the root node
        self.root_node = root_node[0]

    def split_path(self, path: str) -> list[str]:
        return path.removeprefix(self.root_path).split(os.sep)

    def test_snapshot(self, snapshot: str) -> bool:
        return (self.from_snapshot <= snapshot) and (snapshot <= self.to_snapshot)

    def create_tree(self, routine):
        self.init_root()
        for root, dirs, files in os.walk(self.root_path):
            if root == self.root_path:              # Skip root
                continue
            path_parts = self.split_path(root)      # Remove root path component and convert to array
            routine(root, dirs, files, path_parts)  # Perform routine

    def routine_simple(self, root, dirs, files, path_parts, snapshot=None):
        # Find corresponding node for the root
        current = nodes.descend(self.root_node, path_parts)

        # Add folders
        for i in map(lambda x: nodes.create_folder(x), dirs):
            current.appendRow(i)

        # Add files
        for i in map(lambda x: nodes.create_file(x, root, snapshot), files):
            current.appendRow(i)

    def routine_filter(self, path_parts, files, map_fun, filter_fun):
        # Prepare list of items
        items = tuple(filter(filter_fun, tuple(map(map_fun, files))))

        # If there are items to add
        if len(items) > 0:
            # Find corresponding node for the root
            current = nodes.descend(self.root_node, path_parts)

            # Add files
            for i in items:
                current.appendRow(i)

    def routine_unified_unified(self, root, dirs, files, path_parts):
        if self.filter:
            self.routine_filter(path_parts[1:], files,
                                lambda x: nodes.create_file(x, root),
                                lambda x: self.test_snapshot(x[2].text()))
        else:
            self.routine_simple(root, dirs, files, path_parts[1:])

    def routine_bydate_bydate(self, root, dirs, files, path_parts):
        snapshot = path_parts[1]
        if self.filter:
            if self.test_snapshot(snapshot):
                self.routine_filter(path_parts[1:], files,
                                    lambda x: nodes.create_file(x, root, snapshot),
                                    lambda x: True)
        else:
            self.routine_simple(root, dirs, files, path_parts[1:], snapshot)

    def routine_unified_bydate(self, root, dirs, files, path_parts):
        for i in files:
            snapshot = file.get_snapshot(i)
            if not self.filter or (self.filter and self.test_snapshot(snapshot)):
                current = nodes.get_dir_node(self.root_node, snapshot)  # Find corresponding node for the snapshot
                current = nodes.descend(current, path_parts[1:])        # Find corresponding node for the root
                current.appendRow(nodes.create_file(i, root, snapshot)) # Place file in tree

    def routine_bydate_unified(self, root, dirs, files, path_parts):
        snapshot = path_parts[1]
        if not self.filter or (self.filter and self.test_snapshot(snapshot)):
            current = nodes.descend(self.root_node, path_parts[2:])  # Find corresponding node for the root
            for f in files:
                nodes.add_versioned_file(current, f, root, snapshot)

    def routine_empty_dirs(self, root, dirs, files, path_parts):
        if len(dirs) == 0 and len(files) == 0:
            nodes.descend(self.root_node, path_parts[1:])   # Find corresponding node for the root

    def run(self):
        routine = None
        if (self.operation == OperationType.FILE_TREE) or (self.operation == OperationType.FILTERED_TREE):
            # Resolve the required tree type
            if (self.checked[0] == TreeType.UNIFIED) and (self.checked[1] == TreeType.UNIFIED):
                routine = self.routine_unified_unified  # Unified -> unified
            if (self.checked[0] == TreeType.BY_DATE) and (self.checked[1] == TreeType.BY_DATE):
                routine = self.routine_bydate_bydate    # By date -> by date
            if (self.checked[0] == TreeType.UNIFIED) and (self.checked[1] == TreeType.BY_DATE):
                routine = self.routine_unified_bydate   # Unified -> by date
            if (self.checked[0] == TreeType.BY_DATE) and (self.checked[1] == TreeType.UNIFIED):
                routine = self.routine_bydate_unified   # By date -> unified

        if self.operation == OperationType.EMPTY_DIRS:
            routine = self.routine_empty_dirs

        if routine is not None:
            # Finishing tree build
            self.create_tree(routine)   # Build tree
            self.sort_rows()            # Sort nodes

            # Signal object should possess the sending data
            self.signals.operation = self.operation
            self.signals.model = self.model

            # Signal tree update
            self.signals.finished.emit(self.operation, self.model)
