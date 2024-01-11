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


def get_dir_node(parent: QStandardItem, val: str) -> QStandardItem:
    for i in range(0, parent.rowCount()):   # Find existing folder
        if parent.child(i).text() == val:
            return parent.child(i)          # Return existing node

    # If such a folder does not exist
    new_node = create_folder(val)
    parent.appendRow(new_node)

    return new_node[0]                      # Return 1st column of the new node


def descend(parent: QStandardItem, parts: list[str]):
    current = parent
    for i in range(0, len(parts)):
        current = get_dir_node(current, parts[i])       # Get the next node with name from parts
    return current
