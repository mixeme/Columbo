import os

from PyQt5.QtGui import QStandardItem
from pkg import file, icons


TreeNode = list[QStandardItem]      # Type alias for return values


def create_folder(path: str) -> TreeNode:
    return [QStandardItem(icons.IconsLoader.singleton.folder, path),
            QStandardItem("Folder"),
            QStandardItem("---")]