import os

from PyQt5.QtCore import QRunnable
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon

import file


class FileTreeWorker(QRunnable):
    columns = ["Name", "Last modified", "Snapshot"]

    def __init__(self, path, tree_view):
        super().__init__()
        self.path = path.replace("\\", "/")
        self.tree_view = tree_view

        # Load icons
        self.icon_folder = QIcon.fromTheme("folder", QIcon("icons/folder.png"))
        self.icon_file = QIcon.fromTheme("text-x-generic", QIcon("icons/file.png"))

    def create_folder(self, path):
        return [QStandardItem(self.icon_folder, path),
                QStandardItem("Folder"),
                QStandardItem("---")]

    def create_file(self, filename, root):

        return [QStandardItem(self.icon_file, filename),
                QStandardItem(file.get_last_modified(os.path.join(root, filename))),
                QStandardItem(file.get_snapshot(filename))]

    def run(self):
        root_node = self.create_folder(self.path)

        model = QStandardItemModel()
        model.invisibleRootItem().appendRow(root_node)
        model.setHorizontalHeaderLabels(self.columns)

        self.tree_view.setModel(model)
        self.tree_view.header().resizeSection(0, 400)

        for root, dirs, files in os.walk(self.path):
            # Normalize path with path separator "/" and remove root path component
            parts = root.replace("\\", "/").removeprefix(self.path).split("/")

            current = root_node[0]
            for i in range(1, len(parts)):
                found = False
                for j in range(0, current.rowCount()):          # Find existing folder
                    if current.child(j).text() == parts[i]:
                        current = current.child(j)
                        found = True
                        break
                if not found:                                   # If such a folder does not exist
                    new_node = self.create_folder(parts[i])
                    current.appendRow(new_node)
                    current = new_node[0]

            for i in map(lambda x: self.create_folder(x), dirs):
                current.appendRow(i)

            for i in map(lambda x: self.create_file(x, root), files):
                current.appendRow(i)
