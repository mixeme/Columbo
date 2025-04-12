import os

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItem

from core import file
from gui import icons

TreeNode = list[QStandardItem]      # Type alias for return values
PathArray = list[str]               # Type alias for split path string


def create_folder_node(name: str) -> TreeNode:
    return [QStandardItem(icons.IconsLoader.singleton.folder, name),
            QStandardItem("Folder"),
            QStandardItem("---")]


def create_file_node(name: str, root=None, snapshot=None) -> TreeNode:
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


def get_node(parent: QStandardItem, val: str, create_fun) -> QStandardItem:
    """

    :param parent: Parent node
    :param val: Required value as a child of the parent node
    :param create_fun: A function handle for child node creation if it is absent
    :return: Found or created child node
    """

    for i in range(0, parent.rowCount()):   # Find existing folder
        if parent.child(i).text() == val:
            return parent.child(i)          # Return existing node

    # If such a folder does not exist
    new_node = create_fun(val)
    parent.appendRow(new_node)

    return new_node[0]                      # Return 1st column of the new node


def get_dir_node(parent: QStandardItem, val: str) -> QStandardItem:
    """
    Function finds or creates node for `val` inside `parent` node
    :param parent:
    :param val:
    :return:
    """
    return get_node(parent, val, create_folder_node)


def get_file_node(parent: QStandardItem, val: str):
    return get_node(parent, val, create_file_node)


def descend_by_path(parent: QStandardItem, parts: PathArray):
    current = parent
    for i in range(0, len(parts)):
        current = get_dir_node(current, parts[i])       # Get the next node with name from parts
    return current


def add_versioned_file(dir_node, filename, root, snapshot):
    node = get_file_node(dir_node, filename)                # Get or create node with filename in dir_node
    node.appendRow(create_file(filename, root, snapshot))   # Add file version


def is_folder_row(nodes: list[QModelIndex]) -> bool:
    return nodes[0].siblingAtColumn(1).data() == "Folder"
