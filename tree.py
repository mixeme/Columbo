import os
from enum import Enum

from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable
from PyQt5.QtGui import QStandardItemModel, QStandardItem

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

    def __init__(self, path, tree_view, checked):
        super().__init__()
        self.path = path
        self.root_node = None
        self.tree_view = tree_view
        self.sort_rows = None

        # Load icons
        icons.IconsLoader()
        self.checked = checked

    def create_folder(self, path):
        return [QStandardItem(self.icon_folder, path),
                QStandardItem("Folder"),
                QStandardItem("---")]

    def create_file(self, filename, root, snapshot=None):
        if snapshot is None:
            snapshot = file.get_snapshot(filename)

        return [QStandardItem(self.icon_file, filename),
                QStandardItem(file.get_last_modified(os.path.join(root, filename))),
                QStandardItem(snapshot)]

    def create_file2(self, filename):
        return [QStandardItem(self.icon_file, filename),
                QStandardItem("File version"),
                QStandardItem("---")]

    def add_file_composite(self, dir_node, filename, root, snapshot):
        node = self.get_file_node(dir_node, filename)
        node.appendRow(self.create_file(filename, root, snapshot))

    def get_file_node(self, parent, val):
        for i in range(0, parent.rowCount()):  # Find existing folder
            if parent.child(i).text() == val:
                return parent.child(i)  # Return existing node

        # If such a folder does not exist
        new_node = self.create_file2(val)
        parent.appendRow(new_node)

        return new_node[0]              # Return new node

    def init_root(self):
        # Create root node
        root_node = self.create_folder(self.path)
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

    def get_dir_node(self, parent, val):
        for i in range(0, parent.rowCount()):  # Find existing folder
            if parent.child(i).text() == val:
                return parent.child(i)  # Return existing node

        # If such a folder does not exist
        new_node = self.create_folder(val)
        parent.appendRow(new_node)

        return new_node[0]              # Return new node

    def descend(self, parent, parts):
        current = parent
        for i in range(0, len(parts)):
            current = self.get_dir_node(current, parts[i])
        return current

    def create_simple(self):
        root_node = self.init_root()

        for root, dirs, files in os.walk(self.path):
            # Remove root path component and convert to array
            parts = root.removeprefix(self.path).split(os.sep)

            current = self.descend(root_node, parts[1:])        # Find corresponding node for the root

            # Add folders
            for i in map(lambda x: self.create_folder(x), dirs):
                current.appendRow(i)

            # Add files
            for i in map(lambda x: self.create_file(x, root), files):
                current.appendRow(i)

    def create_unified_bydate(self):
        root_node = self.init_root()

        for root, dirs, files in os.walk(self.path):
            # Remove root path component and convert to array
            parts = root.removeprefix(self.path).split(os.sep)

            for i in files:
                snapshot = file.get_snapshot(i)
                current = self.get_dir_node(root_node, snapshot)    # Find corresponding node for the snapshot
                current = self.descend(current, parts[1:])      # Find corresponding node for the root
                current.appendRow(self.create_file(i, root))    # Place file in tree

    def create_bydate_unified(self):
        root_node = self.init_root()

        for root, dirs, files in os.walk(self.path):
            # Remove root path component and convert to array
            parts = root.removeprefix(self.path).split(os.sep)

            if root == self.path:
                continue

            current = self.descend(root_node, parts[2:])  # Find corresponding node for the root

            for f in files:
                self.add_file_composite(current, f, root, parts[1])

    def run(self):
        # Resolve the required tree type
        if self.checked[0] == self.checked[1]:
            # Unified -> unified | by date -> by date
            self.create_simple()
        else:
            if (self.checked[0] == TreeType.UNIFIED) and (self.checked[1] == TreeType.BYDATE):
                # Unified -> by date
                self.create_unified_bydate()
            if (self.checked[0] == TreeType.BYDATE) and (self.checked[1] == TreeType.UNIFIED):
                # By date -> unified
                self.create_bydate_unified()

        # Sort nodes
        self.sort_rows()

        # Update tree
        self.tree_view.update()
