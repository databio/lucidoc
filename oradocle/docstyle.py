""" Docstring styling """

import abc
from .exceptions import OradocleError

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
        if not isinstance(ds, str):
            raise TypeError("Non-string docstring ({})".format(type(ds)))
        return ds


class PycodeDocstringStyler(DocstringStyler):
    """ Style/render docstring by wrapping it in Python code block fences. """
    def __call__(self, ds):
        if not isinstance(ds, str):
            raise TypeError("Non-string docstring ({})".format(type(ds)))
        return "```py{}```".format(ds)


PLAIN_KEY = "plain"
PYCODE_KEY = "pycode"
STYLERS = {
    PLAIN_KEY: PlainDocstringStyler(),
    PYCODE_KEY: PycodeDocstringStyler()
}


class UnknownStylerError(OradocleError):
    """ Exception for request of unsupported styling strategy. """

    def __init__(self, name):
        msg = "{}; choose one: {}".format(name, ", ".join(STYLERS.keys()))
        super(UnknownStylerError, self).__init__(msg)


def get_styler(name):
    """
    Get a docstring styling strategy.

    Parameters
    ----------
    name : str
        Key for a styling strategy.

    Returns
    -------
    oradocle.DocstringStyler
        The styler to which the given name is mapped.

    Raises
    ------
    oradocle.UnknownStylerError
        If given a nonempty name that's not mapped to a styler.

    """
    try:
        return STYLERS[name or PLAIN_KEY]
    except KeyError:
        raise UnknownStylerError(name)
