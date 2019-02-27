""" Helper functions """

import os

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["cleanly_join_lines", "expandpath", "is_callable_like"]


def cleanly_join_lines(lines):
    """
    Single block of text from a collection of lines, accounting for endings.

    :param Iterable[str] lines: collection of lines to join
    :return str: Single block of text of joined lines
    """
    return os.linesep.join(map(lambda l: l.rstrip(os.linesep), lines))


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
    return hasattr(obj, "__call__")
