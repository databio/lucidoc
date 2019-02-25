""" Docstring parsing """

import abc
import itertools
import os
from .exceptions import OradocleError

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["DocstringParser", "RstDocstringParser"]


class DocstringParser(object):
    """ Entity responsible for parsing docstrings """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def description(self, ds):
        """
        Parse the description portion of a docstring

        Parameters
        ----------
        ds : str
            The docstring to parse.

        Returns
        -------
        str
            The description portion of a docstring.

        """
        pass


class RstDocstringParser(DocstringParser):
    """ Parser for ReStructured text docstrings. """

    def description(self, ds):
        if not isinstance(ds, str):
            raise TypeError(
                "Alleged docstring isn't a string, but {}".format(type(ds)))
        return os.linesep.join(itertools.takewhile(
            lambda l: not l.startswith(":"), ds.split(os.linesep)))


RST_KEY = "rst"
STYLERS = {RST_KEY: RstDocstringParser()}


class UnknownParserError(OradocleError):
    """ Exception for request of unsupported parsing strategy. """

    def __init__(self, name):
        msg = "{}; choose one: {}".format(name, ", ".join(STYLERS.keys()))
        super(UnknownParserError, self).__init__(msg)


def get_parser(name):
    """
    Get a docstring parsing strategy.

    Parameters
    ----------
    name : str
        Key for a parsing strategy.

    Returns
    -------
    oradocle.DocstringParser
        The parser to which the given name is mapped.

    Raises
    ------
    oradocle.UnknownParserError
        If given a nonempty name that's not mapped to a parser.

    """
    try:
        return STYLERS[name]
    except KeyError:
        raise UnknownParserError(name)
