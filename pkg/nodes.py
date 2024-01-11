import os

from PyQt5.QtGui import QStandardItem
from pkg import file, icons

icon_loader = None


def create_folder(path):
    return [QStandardItem(icon_loader.folder, path),
            QStandardItem("Folder"),
            QStandardItem("---")]