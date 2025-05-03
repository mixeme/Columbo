from core import types


def get_timestamp(filename: str) -> str:
    """
    :param filename: Name of a file that contains a timestamp as a suffix starting with "_"
    :return: Timestamp designating snapshot
    """
    dot = filename.rfind(".")
    if dot == -1:
        dot = len(filename)

    sep = filename.rfind("_", 0, dot)
    if sep == -1:
        return ""

    return filename[sep + 1:dot]


def get_timestamp_fun(source_type: types.TreeType):
    if source_type == types.TreeType.UNIFIED:
        return lambda x: get_timestamp(x[-1])

    if source_type == types.TreeType.BY_DATE:
        return lambda x: x[0]

    return None
