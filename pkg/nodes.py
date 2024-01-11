from PyQt5.QtGui import QStandardItem

icon_loader = None


def create_folder(path):
    return [QStandardItem(icon_loader.folder, path),
            QStandardItem("Folder"),
            QStandardItem("---")]