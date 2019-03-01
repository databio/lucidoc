""" Helper functions """

import os

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["expandpath", "is_callable_like"]


def expandpath(p):
    """
    Expand environment and user variables contained in filesystem path.

    :param str p: Path in which to perform the variable expansion
    :return str: The expansion of the input path
    """
    return os.path.expanduser(os.path.expandvars(p))


def is_callable_like(obj):
    """
    Determine whether an object is like a callable.

    :param object obj: Object to test for apparent callability.
    :return bool: Whether the given object appears to be a callable.

    """
    return isinstance(obj, property) or hasattr(obj, "__call__")
