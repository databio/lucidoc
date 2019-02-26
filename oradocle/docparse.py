""" Docstring parsing """

import abc
import os
from .exceptions import OradocleError

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["DocstringParser", "RstDocstringParser", "get_parser"]


class DocstringParser(object):
    """ Entity responsible for parsing docstrings """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def split_docstring(self, ds):
        """
        Split a docstring into description and tags portions

        :param str ds: Docstring to split
        :return str, str: Pair of description and tags text
        """
        pass


class RstDocstringParser(DocstringParser):
    """ Parser for ReStructured text docstrings. """

    def split_docstring(self, ds):
        """
        Split a docstring into description and tags portions.

        :param str ds: Docstring to split
        :return str, str: Pair of description and tags text
        :raise TypeError: If argument to docstring parameter is not a string.
        """
        if not isinstance(ds, str):
            raise TypeError(
                "Alleged docstring isn't a string, but {}".format(type(ds)))

        def first_index(s, p):
            for i, x in enumerate(s):
                if p(x):
                    return i
            raise IndexError

        chunks = ds.split(os.linesep)

        try:
            first_tag_index = first_index(chunks, lambda l: l.startswith(":"))
        except IndexError:
            return ds, ""
        else:
            return os.linesep.join(chunks[:first_tag_index]), \
                   os.linesep.join(chunks[first_tag_index:])

    def params(self, ds):
        pass

    def returns(self, ds):
        pass

    def raises(self, ds):
        pass


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

    :param str name: Key for a parsing strategy.
    :return oradocle.DocstringParser: The parser to which the given name is
        mapped.
    :raise oradocle.UnknownParserError: If given a nonempty name that's not
        mapped to a parser.
    """
    try:
        return STYLERS[name]
    except KeyError:
        raise UnknownParserError(name)
