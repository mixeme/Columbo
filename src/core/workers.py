import os

from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
from PyQt5.QtGui import QStandardItemModel

from core import file, node, snapshot, validator
from core.file import is_empty_dir
from core.tree import FileSortFilterProxyModel
from core.types import TreeType, OperationType


# Define signals for events
class Signals(QObject):
    build_finished = pyqtSignal(OperationType, QStandardItemModel)
    clear_finished = pyqtSignal()
    progress = pyqtSignal(str)


class ByDateLogic:
    @staticmethod
    def get_timestamp(path_parts: list[str]):
        if len(path_parts) > 1:
            return path_parts[1]
        else:
            return ""


class FileTreeWorker(QRunnable):
    columns = ["Name", "Last modified", "Snapshot"]
    signals = Signals()

    def __init__(self, root_path: str, checked_options: (TreeType, TreeType), operation: OperationType):
        """

        :param root_path: A path for history storage
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
        self.validator = None
        self.data_model = None
        self.dirs = []
        self.files = []

    def init_root(self) -> None:
        # Create root node
        root_node = node.create_folder_node(self.root_path)

        # Create data model
        model = QStandardItemModel()
        model.invisibleRootItem().appendRow(root_node)
        model.setHorizontalHeaderLabels(FileTreeWorker.columns)

        # Create proxy data model for sorting customization
        proxy_model = FileSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        self.sort_rows = lambda: proxy_model.sort(0, QtCore.Qt.AscendingOrder)
        self.data_model = proxy_model

        # Store 1st column of the root node
        self.root_node = root_node[0]

    def split_path(self, path: str) -> list[str]:
        """

        :param path: Some path as a string
        :return: List of path components split by the OS path separator. The root component `root_path` is removed
                 from the path
        """
        return path.removeprefix(self.root_path).split(os.sep)

    def relative_path(self, path: str) -> str:
        return path.removeprefix(self.root_path)

    def create_tree(self, routine):
        self.init_root()
        for root, dirs, files in os.walk(self.root_path):
            path_parts = self.split_path(root)      # Remove root path component and convert it to array
            routine(root, dirs, files, path_parts)  # Perform routine

    def routine_simple(self, root: str, dirs: list[str], files: list[str], path_parts: list[str], timestamp=None):
        # Find corresponding node for the root
        current = node.descend_by_path(self.root_node, path_parts)

        # Add folders
        for i in map(lambda x: node.create_folder_node(x), dirs):
            current.appendRow(i)

        # Add files
        for i in map(lambda x: node.create_file_node(x, root, timestamp), files):
            current.appendRow(i)

    # def routine_filter(self, files: list[str], path_parts: list[str], map_fun, filter_fun):
    #     # Prepare list of items
    #     items = tuple(filter(filter_fun, tuple(map(map_fun, files))))
    #
    #     # If there are items to add
    #     if len(items) > 0:
    #         # Find corresponding node for the root
    #         current = nodes.descend_by_path(self.root_node, path_parts)
    #
    #         # Add files
    #         for i in items:
    #             current.appendRow(i)

    def new_routine(self, predicate):
        predicate_dir, predicate_file = predicate

        timestamp_fun = snapshot.get_timestamp_fun(self.checked_options[0])

        file_parts = [i.split(os.sep) for i in self.files]

        # Normalize path
        if self.checked_options0[0] == TreeType.UNIFIED:
            for i in file_parts:
                i.insert(0, )

        for dir_path in self.dirs:
            if predicate_dir.validate(dir_path):
                # Split directory path to components
                parts = dir_path.split(os.sep)

                # Find corresponding node for the root
                current = node.descend_by_path(self.root_node, parts[1:-2])

                current.appendRow(node.create_folder_node(parts[-1]))

        for file_path in self.files:
            if predicate_file.validate(file_path):
                # Split directory path to components
                parts = file_path.split(os.sep)

                # Find corresponding node for the root
                current = node.descend_by_path(self.root_node, parts[1:-2])

                current.appendRow(node.create_file_node(parts[-1]))

    def routine_filter2(self, files: list[str], path_parts: list[str], filter_fun, map_fun):
        # Prepare list of items
        items = tuple(map(map_fun, tuple(filter(filter_fun, files))))

        # If there are items to add
        if len(items) > 0:
            # Find corresponding node for the root
            current = node.descend_by_path(self.root_node, path_parts)

            # Add files
            for i in items:
                current.appendRow(i)

    def routine_unified_unified(self, root: str, dirs: list[str], files: list[str], path_parts: list[str]):
        if self.validator is None:
            self.routine_simple(root, dirs, files, path_parts[1:])
        else:
            self.routine_filter2(files, path_parts[1:],
                                 lambda x: self.validator.validate_timestamp(x),
                                 lambda x: node.create_file_node(x, root))

    def routine_bydate_bydate(self, root: str, dirs: list[str], files: list[str], path_parts: list[str]):
        timestamp = ByDateLogic.get_timestamp(path_parts)
        if self.validator is None:
            self.routine_simple(root, dirs, files, path_parts[1:], timestamp)
        else:
            if self.validator.validate_timestamp(timestamp):
                self.routine_filter2(files, path_parts[1:],
                                     lambda x: True,
                                     lambda x: node.create_file_node(x, root, timestamp))

    def routine_unified_bydate(self, root: str, dirs: str, files: list[str], path_parts: list[str]):
        for f in files:
            timestamp = snapshot.get_timestamp(f)
            if self.validator is None or self.validator.validate_timestamp(timestamp):
                # Find corresponding node for the snapshot
                snapshot_node = node.get_dir_node(self.root_node, timestamp)

                # Get sibling item with snapshot data
                sibling = snapshot_node.index().siblingAtColumn(2)

                # Set a snapshot comment at the snapshot node if it is absent
                if sibling.data() == "---":
                    sibling.model().itemFromIndex(sibling).setText(timestamp)

                # Find corresponding node for the root
                parent_node = node.descend_by_path(snapshot_node, path_parts[1:])

                # Place file in tree
                parent_node.appendRow(node.create_file_node(f, root, timestamp))

    def routine_bydate_unified(self, root: str, dirs: str, files: list[str], path_parts: list[str]):
        timestamp = ByDateLogic.get_timestamp(path_parts)
        if self.validator is None or (self.validator.validate_timestamp(timestamp)
                                      and self.validator.validate_root(path_parts)):
            current = node.descend_by_path(self.root_node, path_parts[2:])  # Find corresponding node for the root
            for f in files:
                node.add_file_version(current, f, root, timestamp)

    def routine_empty_dirs(self, root: str, dirs: list[str], files: list[str], path_parts: list[str]):
        if len(dirs) == 0 and len(files) == 0:
            node.descend_by_path(self.root_node, path_parts[1:])   # Find corresponding node for the root

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
            self.signals.model = self.data_model

            # Signal tree update
            self.signals.build_finished.emit(self.operation, self.data_model)


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
        self.signals.clear_finished.emit()


class ClearSnapshotWorker(QRunnable):
    signals = Signals()

    def __init__(self, root_path: str, tester: validator.SnapshotValidator):
        super().__init__()
        self.root_path = root_path
        self.tester = tester

    def run(self) -> None:
        for root, dirs, files in os.walk(self.root_path):
            for f in files:
                if self.tester.test_file(root.removeprefix(self.root_path), f):
                    path = os.path.join(root, f)
                    try:
                        os.remove(path)
                        self.signals.progress.emit("Delete " + path)
                    except OSError:
                        self.signals.progress.emit("Failed to delete " + path)
        self.signals.clear_finished.emit()
