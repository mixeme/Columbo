from enum import Enum


class TreeType(Enum):
    UNIFIED = 0
    BY_DATE = 1


class OperationType(Enum):
    FILE_TREE = 0
    FILTERED_TREE = 1
    EMPTY_DIRS = 2
