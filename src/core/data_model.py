from PyQt5 import QtCore

import os
from core import node
from core.types import ViewDirection


def restore_path(root, view_direction: ViewDirection, selected_nodes) -> (str, str):
    index = selected_nodes[0]            # Get the selected index
    snapshot = selected_nodes[2].data()  # Get snapshot name

    # Go up for a versioned file (By date -> Unified)
    if view_direction.by_date_to_unified() \
            and (not node.is_folder_row(selected_nodes)):
        index = index.parent()

    selected_item = index.data()         # Get data of the selected index
    selected_path = selected_item        # Prepare selected path

    index = index.parent()  # Get its parent
    while index.isValid():  # Combine a path to the selected item
        parent_item = index.data()  # Get parent name

        # If we reach the root
        if parent_item == root:
            # Add snapshot to the path for By date -> Unified
            if view_direction.by_date_to_unified() \
                    and (not node.is_folder_row(selected_nodes)):
                parent_item = os.path.join(parent_item, snapshot)

            # Remove snapshot from the path for Unified -> By date
            if view_direction.unified_to_by_date():
                selected_path = selected_path[selected_path.find(os.sep) + 1:]

        selected_path = os.path.join(parent_item, selected_path)
        index = index.parent()

    return selected_path, selected_item


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
