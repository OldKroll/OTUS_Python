"""
TODO:

The function `add` accepts two arguments and returns a value, they all have the same type.
The type can only be str or int (or their subclasses).
"""


def add[T: (str, int)](a: T, b: T) -> T:  # type: ignore
    return a
