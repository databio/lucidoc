""" Docstring styling """

import abc
from .exceptions import OradocleError

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["DocstringStyler", "PycodeDocstringStyler", "get_styler"]


class DocstringStyler(object):
    """ How to style/render docstrings """
    @abc.abstractmethod
    def __call__(self, ds):
        pass


class PycodeDocstringStyler(DocstringStyler):
    """ Style/render docstring by wrapping it in Python code block fences. """
    def __call__(self, ds):
        if not isinstance(ds, str):
            raise TypeError("Non-string docstring ({})".format(type(ds)))
        return ds


PYCODE_KEY = "pycode"
STYLERS = {PYCODE_KEY: PycodeDocstringStyler()}


class UnknownStylerError(OradocleError):
    def __init__(self, name):
        msg = "{}; choose one: {}".format(name, ", ".join(STYLERS.keys()))
        super(UnknownStylerError, self).__init__(msg)


def get_styler(name):
    try:
        return STYLERS[name]
    except KeyError:
        raise UnknownStylerError(name)

