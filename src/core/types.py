from enum import Enum

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItem

TreeNode = list[QStandardItem]      # Type alias for return values
TreeRow = list[QModelIndex]         # Type alias for row entry
PathArray = list[str]               # Type alias for split path string


class TreeType(Enum):
    UNIFIED = 0
    BY_DATE = 1


class OperationType(Enum):
    FILE_TREE = 0
    FILTERED_TREE = 1
    EMPTY_DIRS = 2


