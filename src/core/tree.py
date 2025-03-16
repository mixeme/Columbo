import os

from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable, pyqtSignal, QObject
from PyQt5.QtGui import QStandardItemModel

from core import file, nodes
from core.nodes import PathArray
from core.types import TreeType, OperationType


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

    def __init__(self, root_path: str, checked_options: (TreeType, TreeType), operation: OperationType):
        """

        :param root_path: A path for history storage
        :param sub_path: A sub-path inside history storage
        :param checked_options: A tuple of the (source,  target) tree presentation
        :param operation: A requested operation
        """
        super().__init__()
        # Store input values
        self.root_path = root_path
        self.checked_options = checked_options
        self.operation = operation

        # Declare fields
        self.root_node = None
        self.sort_rows = None
        self.tester = None
        self.model = None

    def set_filter(self, tester: file.SnapshotTester):
        self.tester = tester

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

    def split_path(self, path: str) -> PathArray:
        """

        :param path: Some path as a string
        :return: List of path components split by the OS path separator. The root component `root_path` is removed
                 from the path
        """
        return path.removeprefix(self.root_path).split(os.sep)

    def create_tree(self, routine):
        self.init_root()
        for root, dirs, files in os.walk(self.root_path):
            path_parts = self.split_path(root)      # Remove root path component and convert to array
            routine(root, dirs, files, path_parts)  # Perform routine

    def routine_simple(self, root: str, dirs: PathArray, files: PathArray, path_parts: PathArray, snapshot=None):
        # Find corresponding node for the root
        current = nodes.descend(self.root_node, path_parts)

        # Add folders
        for i in map(lambda x: nodes.create_folder(x), dirs):
            current.appendRow(i)

        # Add files
        for i in map(lambda x: nodes.create_file(x, root, snapshot), files):
            current.appendRow(i)

    def routine_filter(self, path_parts: PathArray, files: list[str], map_fun, filter_fun):
        # Prepare list of items
        items = tuple(filter(filter_fun, tuple(map(map_fun, files))))

        # If there are items to add
        if len(items) > 0:
            # Find corresponding node for the root
            current = nodes.descend(self.root_node, path_parts)

            # Add files
            for i in items:
                current.appendRow(i)

    def routine_unified_unified(self, root: str, dirs: list[str], files: list[str], path_parts: PathArray):
        if self.tester:
            self.routine_filter(path_parts[1:], files,
                                lambda x: nodes.create_file(x, root),
                                lambda x: self.tester.test_snapshot(x[2].text()))
        else:
            self.routine_simple(root, dirs, files, path_parts[1:])

    def routine_bydate_bydate(self, root: str, dirs: list[str], files: list[str], path_parts: PathArray):
        if len(path_parts) > 1:
            snapshot = path_parts[1]
        else:
            snapshot = ""
        if self.tester:
            if self.tester.test_snapshot(snapshot):
                self.routine_filter(path_parts[1:], files,
                                    lambda x: nodes.create_file(x, root, snapshot),
                                    lambda x: True)
        else:
            self.routine_simple(root, dirs, files, path_parts[1:], snapshot)

    def routine_unified_bydate(self, root: str, dirs, files: list[str], path_parts: list[str]):
        for i in files:
            snapshot = file.get_snapshot(i)
            if not self.tester or (self.tester and self.tester.test_snapshot(snapshot)):
                # Find corresponding node for the snapshot
                snapshot_node = nodes.get_dir_node(self.root_node, snapshot)

                # Get sibling item with snapshot data
                sibling = snapshot_node.index().siblingAtColumn(2)

                # Set a snapshot comment at the snapshot node if it is absent
                if sibling.data() == "---":
                    sibling.model().itemFromIndex(sibling).setText(snapshot)

                # Find corresponding node for the root
                parent_node = nodes.descend(snapshot_node, path_parts[1:])

                # Place file in tree
                parent_node.appendRow(nodes.create_file(i, root, snapshot))

    def routine_bydate_unified(self, root: str, dirs, files: list[str], path_parts: list[str]):
        if len(path_parts) > 1:
            snapshot = path_parts[1]
        else:
            snapshot = ""
        if not self.tester or (self.tester
                               and self.tester.test_snapshot(snapshot)
                               and self.tester.test_root(path_parts)):
            current = nodes.descend(self.root_node, path_parts[2:])  # Find corresponding node for the root
            for f in files:
                nodes.add_versioned_file(current, f, root, snapshot)

    def routine_empty_dirs(self, root: str, dirs: list[str], files: list[str], path_parts: list[str]):
        if len(dirs) == 0 and len(files) == 0:
            nodes.descend(self.root_node, path_parts[1:])   # Find corresponding node for the root

    def run(self) -> None:
        routine = None
        if (self.operation == OperationType.FILE_TREE) or (self.operation == OperationType.FILTERED_TREE):
            # Resolve the required tree type
            if (self.checked_options[0] == TreeType.UNIFIED) and (self.checked_options[1] == TreeType.UNIFIED):
                routine = self.routine_unified_unified  # Unified -> unified
            if (self.checked_options[0] == TreeType.BY_DATE) and (self.checked_options[1] == TreeType.BY_DATE):
                routine = self.routine_bydate_bydate    # By date -> by date
            if (self.checked_options[0] == TreeType.UNIFIED) and (self.checked_options[1] == TreeType.BY_DATE):
                routine = self.routine_unified_bydate   # Unified -> by date
            if (self.checked_options[0] == TreeType.BY_DATE) and (self.checked_options[1] == TreeType.UNIFIED):
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
