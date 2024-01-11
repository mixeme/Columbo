import os

from PyQt5.QtGui import QStandardItem
from pkg import file, icons


TreeNode = list[QStandardItem]      # Type alias for return values


def create_folder(path: str) -> TreeNode:
    return [QStandardItem(icons.IconsLoader.singleton.folder, path),
            QStandardItem("Folder"),
            QStandardItem("---")]


def create_file(filename: str, root=None, snapshot=None) -> TreeNode:
    if root is None:
        mod_date = "File version"
        snapshot = "---"
    else:
        mod_date = file.get_last_modified(os.path.join(root, filename))

    if snapshot is None:
        snapshot = file.get_snapshot(filename)

    return [QStandardItem(icons.IconsLoader.singleton.file, filename),
            QStandardItem(mod_date),
            QStandardItem(snapshot)]
