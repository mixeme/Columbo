from PyQt5 import QtCore


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
