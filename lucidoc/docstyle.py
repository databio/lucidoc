""" Docstring styling """

import abc
from .exceptions import LucidocError

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["DocstringStyler", "PycodeDocstringStyler", "get_styler"]


class DocstringStyler(object):
    """ How to style/render docstrings """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self, ds):
        pass


class PlainDocstringStyler(DocstringStyler):
    """ Style/render docstring by simply echoing it. """

    def __call__(self, ds):
        """
        Echo a docstring for the plainest of plain styling

        :param str ds: docstring to render
        :return str: same docstring as input
        """
        if not isinstance(ds, str):
            raise TypeError("Non-string docstring ({})".format(type(ds)))
        return ds


class PycodeDocstringStyler(DocstringStyler):
    """ Style/render docstring by wrapping it in Python code block fences. """

    def __call__(self, ds):
        """
        Render docstring as Python code block.

        :param str ds: docstring to render
        :return str: rendition of given docstring
        """
        if not isinstance(ds, str):
            raise TypeError("Non-string docstring ({})".format(type(ds)))
        return "```py{}```".format(ds)


PLAIN_KEY = "plain"
PYCODE_KEY = "pycode"
STYLERS = {
    PLAIN_KEY: PlainDocstringStyler(),
    PYCODE_KEY: PycodeDocstringStyler()
}


class UnknownStylerError(LucidocError):
    """ Exception for request of unsupported styling strategy. """

    def __init__(self, name):
        """
        Create exception for request of styler of unknown name.

        :param str name: name/key for desired styler / styling strategy,
            that's not mapped to an instance and is thus problematic
        """
        msg = "{}; choose one: {}".format(name, ", ".join(STYLERS.keys()))
        super(UnknownStylerError, self).__init__(msg)


def get_styler(name):
    """
    Get a docstring styling strategy.

    :param str name: name/key of desired styling strategy
    :return lucidoc.DocstringStyler: styler to which given name is mapped.
    :raise lucidoc.UnknownStylerError: if given a nonempty name that's not
        mapped to a styler.
    """
    try:
        return STYLERS[name or PLAIN_KEY]
    except KeyError:
        raise UnknownStylerError(name)
