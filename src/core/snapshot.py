from core import types

# Constant for delimiter
timestamp_delimiter = "_"


def find_dot(filename: str) -> int:
    # Find dot position
    dot = filename.rfind(".")

    if dot == -1:
        # If no dot, return end of string
        dot = len(filename)

    return dot


def get_timestamp(filename: str) -> str:
    """
    :param filename: Name of a file that contains a timestamp as a suffix starting with "_"
    :return: Timestamp designating snapshot
    """
    # Find dot position
    dot = find_dot(filename)

    # Find delimiter position
    sep = filename.rfind(timestamp_delimiter, 0, dot)
    if sep == -1:
        # If no delimiter, return empty timestamp
        return ""

    # Cut suffix
    return filename[sep + 1:dot]


def set_timestamp(filename: str, timestamp: str) -> str:
    dot = find_dot(filename)
    return filename[:dot] + timestamp_delimiter + timestamp + filename[dot:]


def get_timestamp_fun(source_type: types.TreeType):
    if source_type == types.TreeType.UNIFIED:
        return lambda x: get_timestamp(x[-1])

    if source_type == types.TreeType.BY_DATE:
        return lambda x: x[0]

    return None
