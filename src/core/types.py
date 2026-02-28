from enum import Enum
from typing import Final

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItem

TreeNode = list[QStandardItem]      # Type alias for return values
TreeRow = list[QModelIndex]         # Type alias for row entry


class TreeType(Enum):
    UNIFIED = 0
    BY_DATE = 1


class OperationType(Enum):
    FULL_TREE = 0
    FILTERED_TREE = 1
    EMPTY_DIRS = 2
    DELETE_SNAPSHOTS = 3
    DELETE_EMPTY_DIRS = 4


class ViewDirection:
    def __init__(self, source: TreeType, target: TreeType) -> None:
        self.source: Final[TreeType] = source
        self.target: Final[TreeType] = target

    def unified_to_by_date(self) -> bool:
        return (self.source == TreeType.UNIFIED) and (self.target == TreeType.BY_DATE)

    def by_date_to_unified(self) -> bool:
        return (self.source == TreeType.BY_DATE) and (self.target == TreeType.UNIFIED)
