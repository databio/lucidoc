""" Helper functions """

import os

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["expandpath", "is_callable_like"]


def expandpath(p):
    """
    Expand environment and user variables contained in filesystem path.

    Parameters
    ----------
    p : str
        Path in which to perform the variable expansion

    Returns
    -------
    str
        The expansion of the input path

    """
    return os.path.expanduser(os.path.expandvars(p))


def is_callable_like(obj):
    """
    Determine whether an object is like a callable.

    Parameters
    ----------
    obj : object
        Object to test for apparent callability.

    Returns
    -------
    bool
        Whether the given object appears to be a callable.

    """
    return hasattr(obj, "__call__")
