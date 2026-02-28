from PyQt5 import QtCore

from PyQt5.QtCore import QModelIndex

from core import node


def gather_path(node_index: QModelIndex) -> list[str]:
    path = [node_index.data()]                  # Prepare selected path, get data of the selected index

    parent_index = node_index.parent()          # Get parent
    while parent_index.isValid():               # Loop for gathering path components
        current_index = parent_index            # Store parent
        parent_index = current_index.parent()   # Go up

        if node.is_versioned_file_row(current_index):
            # Skip a versioned file (by date -> Unified)
            continue
        else:
            # Collect a component otherwise
            path.append(current_index.data())

    # Reverse components order: root should be the first component
    path.reverse()
    return path


def gather_subnodes_path(node_index: QModelIndex) -> list[list[str]]:
    nodes: list[QModelIndex] = node.traverse_depth_first(node_index, True)
    return [gather_path(n) for n in nodes]


# Class for sorting tree view
class FileSortFilterProxyModel(QtCore.QSortFilterProxyModel):
    def lessThan(self, left, right):
        # Retrieve file names
        left_name = left.data()
        right_name = right.data()
        # Retrieve file last modified dates
        left_date = left.siblingAtColumn(1).data()
        right_date = right.siblingAtColumn(1).data()
        # Retrieve snapshot timestamps
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
        # This is the case "by date -> unified"
        if left_name == right_name:
            return left_snapshot < right_snapshot   # Compare timestamp of snapshots

        # All other cases
        return left_name < right_name
