import os
from enum import Enum

from PyQt5.QtCore import QRunnable
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon

import file


class TreeType(Enum):
    UNIFIED = 0
    BYDATE = 1


class FileTreeWorker(QRunnable):
    columns = ["Name", "Last modified", "Snapshot"]

    def __init__(self, path, tree_view, checked):
        super().__init__()
        self.path = path.replace(os.sep, "/")
        self.tree_view = tree_view

        # Load icons
        self.icon_folder = QIcon.fromTheme("folder", QIcon("icons/folder.png"))
        self.icon_file = QIcon.fromTheme("text-x-generic", QIcon("icons/file.png"))
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

    def create_file(self, filename, root):
        return self.create_file2(filename, root, file.get_snapshot(filename))

    def init_root(self):
        # Create root node
        root_node = self.create_folder(self.path)
        # Create data model
        model = QStandardItemModel()
        model.invisibleRootItem().appendRow(root_node)
        model.setHorizontalHeaderLabels(self.columns)
        # Setup QTreeView
        self.tree_view.setModel(model)
        self.tree_view.header().resizeSection(0, 400)

        return root_node[0]

    def get_node(self, parent, val):
        for i in range(0, parent.rowCount()):  # Find existing folder
            if parent.child(i).text() == val:
                return parent.child(i)

        # If such a folder does not exist
        new_node = self.create_folder(val)
        parent.appendRow(new_node)
        parent.sortChildren(0)
        return new_node[0]

    def create_tree(self):
        root_node = self.init_root()

        for root, dirs, files in os.walk(self.path):
            # Normalize path with path separator "/" and remove root path component
            parts = root.replace("\\", "/").removeprefix(self.path).split("/")
            # Find corresponding node for the root
            current = root_node
            for i in range(1, len(parts)):
                current = self.get_node(current, parts[i])
            # Add folders
            for i in map(lambda x: self.create_folder(x), dirs):
                current.appendRow(i)
            # Add files
            for i in map(lambda x: self.create_file(x, root), files):
                current.appendRow(i)

    def create_unified_bydate(self):
        root_node = self.init_root()

        for root, dirs, files in os.walk(self.path):
            # Normalize path with path separator "/" and remove root path component
            parts = root.replace("\\", "/").removeprefix(self.path).split("/")
            for i in files:
                snapshot = file.get_snapshot(i)
                current = root_node
                # Find corresponding node for the snapshot
                current = self.get_node(current, snapshot)
                # Find corresponding node for the root
                for j in range(1, len(parts)):
                    current = self.get_node(current, parts[j])
                # Place file in tree
                current.appendRow(self.create_file(i, root))
        # Sort snapshot nodes
        root_node.sortChildren(0)

    def create_bydate_unified(self):
        root_node = self.init_root()

        for root, dirs, files in os.walk(self.path):
            # Normalize path with path separator "/" and remove root path component
            parts = root.replace("\\", "/").removeprefix(self.path).split("/")

            if root == self.path:
                continue
            snapshot = parts[1]
            # Find corresponding node for the root
            current = root_node
            for i in range(2, len(parts)):
                current = self.get_node(current, parts[i])
            # Add folders
            #for i in map(lambda x: self.create_folder(x), dirs):
            #    current.appendRow(i)
            # Add files
            for i in map(lambda x: self.create_file2(x, root, snapshot), files):
                current.appendRow(i)
            current.sortChildren(0)

    def run(self):
        if self.checked[0] == self.checked[1]:
            self.create_tree()
        else:
            if (self.checked[0] == TreeType.UNIFIED) and (self.checked[1] == TreeType.BYDATE):
                self.create_unified_bydate()
            if (self.checked[0] == TreeType.BYDATE) and (self.checked[1] == TreeType.UNIFIED):
                self.create_bydate_unified()
        self.tree_view.update()
