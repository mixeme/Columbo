import os

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItem

import core.snapshot
from core import file
from gui import icons


def create_folder_node(name: str) -> TreeNode:
    return [QStandardItem(icons.IconsLoader.singleton.folder, name),
            QStandardItem("Folder"),
            QStandardItem("---")]


def create_file_node(name: str, root=None, timestamp=None) -> TreeNode:
    if root is None:
        # If a root of file is not specified, then consider a node as a versioned file
        modification_date = "File version"
        timestamp = "---"
    else:
        # Otherwise, retrieve the last modified date from the filesystem
        modification_date = file.get_last_modified(os.path.join(root, name))

    if timestamp is None:
        # If a timestamp is not specified, retrieve it from a filename
        timestamp = core.snapshot.get_snapshot(name)

    # Create and return file node
    return [QStandardItem(icons.IconsLoader.singleton.file, name),
            QStandardItem(modification_date),
            QStandardItem(timestamp)]


def is_folder_row(nodes: TreeRow) -> bool:
    """
    Test tree row whether it is a folder row or not
    :param nodes: List of node indices in a row
    :return: Whether the specified row designates a folder
    """
    return nodes[1].data() == "Folder"


def get_node(parent: QStandardItem, val: str, create_fun) -> QStandardItem:
    """
    Function finds or creates a node (with `create_fun`) for `val` inside a `parent` node
    :param parent: Parent node
    :param val: Required value for a child of the specified parent node
    :param create_fun: A function handle for a child node creation if it is absent
    :return: Found or created child node
    """

    for i in range(0, parent.rowCount()):   # Find existing child nodes
        if parent.child(i).text() == val:
            return parent.child(i)          # Return existing node

    # If such a child does not exist
    new_node = create_fun(val)
    parent.appendRow(new_node)

    return new_node[0]                      # Return 1st column of the new node


def get_dir_node(parent: QStandardItem, val: str) -> QStandardItem:
    """
    Function finds or creates a directory node for `val` inside a `parent` node
    :param parent: Parent node
    :param val: Required value for a directory node of the specified parent node
    :return: Found or created child directory node
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
    node.appendRow(create_file_node(filename, root, snapshot))   # Add file version
