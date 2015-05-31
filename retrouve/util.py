"""
Utility functions
"""

def merge_dicts(a, b):
    """
    Merge two dictionaries, overwriting the keys from dict `a` with those from
    dict `b` should they conflict.
    :param a: dict
    :param b: dict
    :return: dict
    """
    temp = a.copy()
    temp.update(b)
    return temp
