import os
from enum import Enum

from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable
from PyQt5.QtGui import QStandardItemModel

from pkg import file, icons, nodes


class TreeType(Enum):
    UNIFIED = 0
    BYDATE = 1


class OperatioType(Enum):
    FILE_TREE = 0
    EMPTY_DIRS = 1


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


class FileTreeWorker(QRunnable):
    columns = ["Name", "Last modified", "Snapshot"]

    def __init__(self, root_path, tree_view, checked_options, operation: OperatioType):
        super().__init__()
        # Store input values
        self.root_path = root_path
        self.tree_view = tree_view
        self.checked = checked_options
        self.operation = operation

        # Declare fields
        self.root_node = None
        self.sort_rows = None
        self.end_update = None
        self.filter = False
        self.from_snapshot = None
        self.to_snapshot = None

        # Load icons
        icons.IconsLoader()

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
        model.beginResetModel()

        # Create proxy data model for sorting customisation
        proxy_model = FileSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        self.sort_rows = lambda: proxy_model.sort(0, QtCore.Qt.AscendingOrder)
        self.end_update = lambda: model.endResetModel()

        # Setup QTreeView
        self.tree_view.setModel(proxy_model)
        self.tree_view.header().resizeSection(0, 400)

        # Store 1st column of the root node
        self.root_node = root_node[0]

    def split_path(self, path: str) -> list[str]:
        return path.removeprefix(self.root_path).split(os.sep)

    def create_tree(self, routine):
        self.init_root()
        for root, dirs, files in os.walk(self.root_path):
            if root == self.root_path:  # Skip root
                continue
            routine(root, dirs, files)

    def routine_simple(self, root, dirs, files, path_parts, snapshot=None):
        # Find corresponding node for the root
        current = nodes.descend(self.root_node, path_parts[1:])

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

    def routine_unified_unified(self, root, dirs, files):
        # Remove root path component and convert path to string array
        path_parts = self.split_path(root)

        if self.filter:
            file_nodes = list(map(lambda x: nodes.create_file(x, root), files))
            filtered_nodes = []
            for i in file_nodes:
                snapshot = i[2].text()
                if (self.from_snapshot <= snapshot) and (snapshot <= self.to_snapshot):
                    filtered_nodes.append(i)
            if len(filtered_nodes) > 0:
                # Find corresponding node for the root
                current = nodes.descend(self.root_node, path_parts[1:])

                # Add files
                for i in filtered_nodes:
                    current.appendRow(i)
        else:
            self.routine_simple(root, dirs, files, path_parts)

    def routine_bydate_bydate(self, root, dirs, files):
        # Remove root path component and convert path to string array
        path_parts = self.split_path(root)

        if self.filter:
            snapshot = path_parts[1]
            if (self.from_snapshot <= snapshot) and (snapshot <= self.to_snapshot):
                # Find corresponding node for the root
                current = nodes.descend(self.root_node, path_parts[1:])

                # Add files
                for i in map(lambda x: nodes.create_file(x, root, snapshot), files):
                    current.appendRow(i)
        else:
            self.routine_simple(root, dirs, files, path_parts, path_parts[1])

    def routine_unified_bydate(self, root, dirs, files):
        # Remove root path component and convert to array
        path_parts = self.split_path(root)

        for i in files:
            snapshot = file.get_snapshot(i)
            current = nodes.get_dir_node(self.root_node, snapshot)  # Find corresponding node for the snapshot
            current = nodes.descend(current, path_parts[1:])        # Find corresponding node for the root
            current.appendRow(nodes.create_file(i, root))           # Place file in tree

    def routine_bydate_unified(self, root, dirs, files):
        if root == self.root_path:  # Skip root
            return

        # Remove root path component and convert to array
        path_parts = self.split_path(root)

        current = nodes.descend(self.root_node, path_parts[2:])  # Find corresponding node for the root
        for f in files:
            nodes.add_versioned_file(current, f, root, path_parts[1])

    def routine_empty_dirs(self, root, dirs, files):
        if len(dirs) == 0 and len(files) == 0:
            # Remove root path component and convert to array
            path_parts = self.split_path(root)

            # Find corresponding node for the root
            nodes.descend(self.root_node, path_parts[1:])

    def run(self):
        if self.operation == OperatioType.FILTER:
            return

        routine = None
        if self.operation == OperatioType.FILE_TREE:
            # Resolve the required tree type
            if (self.checked[0] == TreeType.UNIFIED) and (self.checked[1] == TreeType.UNIFIED):
                routine = self.routine_unified_unified           # Unified -> unified
            if (self.checked[0] == TreeType.BYDATE) and (self.checked[1] == TreeType.BYDATE):
                routine = self.routine_bydate_bydate    # By date -> by date
            if (self.checked[0] == TreeType.UNIFIED) and (self.checked[1] == TreeType.BYDATE):
                routine = self.routine_unified_bydate   # Unified -> by date
            if (self.checked[0] == TreeType.BYDATE) and (self.checked[1] == TreeType.UNIFIED):
                routine = self.routine_bydate_unified   # By date -> unified

        if self.operation == OperatioType.EMPTY_DIRS:
            routine = self.routine_empty_dirs

        if routine is not None:
            # Finishing tree build
            self.create_tree(routine)   # Build tree
            self.sort_rows()            # Sort nodes
            self.end_update()           # Rebuild tree
