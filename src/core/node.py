from PyQt5.QtGui import QStandardItem

from core.types import TreeNode, TreeRow, TreeType
from gui import icons


def create_folder_node(name: str) -> TreeNode:
    # Create and return directory node
    return [QStandardItem(icons.IconsLoader.singleton.folder, name),
            QStandardItem("Folder"),
            QStandardItem("---")]


def create_file_node(name: str, last_modified="File version", timestamp="---") -> TreeNode:
    # Create and return file node
    return [QStandardItem(icons.IconsLoader.singleton.file, name),
            QStandardItem(last_modified),
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


def descend_by_path(parent: QStandardItem, path_parts: list[str]):
    current = parent
    for part in path_parts:
        # Get the next node with a name from path parts
        current = get_node(current, part, create_folder_node)
    return current


def add_file_node(parent: QStandardItem, tree_type: (TreeType, TreeType), filename, last_mod_date, timestamp):
    # Unpack types of trees
    source_tree, target_tree = tree_type

    if source_tree == TreeType.BY_DATE and target_tree == TreeType.UNIFIED:
        # Get or create a versioned file node inside the specified directory node
        parent = get_node(parent, filename, create_file_node)

    # Create node and append it to the tree
    parent.appendRow(create_file_node(filename, last_mod_date, timestamp))
