import os
from enum import Enum

from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable
from PyQt5.QtGui import QStandardItemModel

from pkg import file, icons, nodes


class TreeType(Enum):
    UNIFIED = 0
    BYDATE = 1


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

    def __init__(self, root_path, tree_view, checked_options):
        super().__init__()
        # Store input values
        self.root_path = root_path
        self.tree_view = tree_view
        self.checked = checked_options

        # Declare fields
        self.root_node = None
        self.sort_rows = None

        # Load icons
        icons.IconsLoader()
        self.checked = checked

    def init_root(self):
        # Create root node
        root_node = nodes.create_folder(self.root_path)

        # Create data model
        model = QStandardItemModel()
        model.invisibleRootItem().appendRow(root_node)
        model.setHorizontalHeaderLabels(self.columns)
        # Create proxy data model to customizing sorting
        proxy_model = FileSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        self.sort_rows = lambda: proxy_model.sort(0, QtCore.Qt.AscendingOrder)
        # Setup QTreeView
        self.tree_view.setModel(proxy_model)
        self.tree_view.header().resizeSection(0, 400)
        # Store root node
        self.root_node = root_node[0]

        return self.root_node

    def create_simple(self):
        root_node = self.init_root()

        for root, dirs, files in os.walk(self.path):
            # Remove root path component and convert to array
            parts = root.removeprefix(self.path).split(os.sep)

            current = nodes.descend(root_node, parts[1:])        # Find corresponding node for the root

            # Add folders
            for i in map(lambda x: nodes.create_folder(x), dirs):
                current.appendRow(i)

            # Add files
            for i in map(lambda x: nodes.create_file(x, root), files):
                current.appendRow(i)

    def create_unified_bydate(self):
        root_node = self.init_root()

        for root, dirs, files in os.walk(self.path):
            # Remove root path component and convert to array
            parts = root.removeprefix(self.path).split(os.sep)

            for i in files:
                snapshot = file.get_snapshot(i)
                current = nodes.get_dir_node(root_node, snapshot)    # Find corresponding node for the snapshot
                current = nodes.descend(current, parts[1:])      # Find corresponding node for the root
                current.appendRow(nodes.create_file(i, root))    # Place file in tree

    def create_bydate_unified(self):
        root_node = self.init_root()

        for root, dirs, files in os.walk(self.path):
            # Remove root path component and convert to array
            parts = root.removeprefix(self.path).split(os.sep)

            if root == self.path:
                continue

            current = nodes.descend(root_node, parts[2:])  # Find corresponding node for the root

            for f in files:
                nodes.add_versioned_file(current, f, root, parts[1])

    def run(self):
        # Resolve the required tree type
        if self.checked[0] == self.checked[1]:
            self.create_simple()                # Unified -> unified | by date -> by date
        else:
            if (self.checked[0] == TreeType.UNIFIED) and (self.checked[1] == TreeType.BYDATE):
                self.create_unified_bydate()    # Unified -> by date
            if (self.checked[0] == TreeType.BYDATE) and (self.checked[1] == TreeType.UNIFIED):
                self.create_bydate_unified()    # By date -> unified
        # Finishing tree build
        self.sort_rows()            # Sort nodes
        self.tree_view.update()     # Update tree
