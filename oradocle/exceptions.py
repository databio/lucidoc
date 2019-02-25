""" Custom package exceptions """

import abc

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


class OradocleError(Exception):
    __metaclass__ = abc.ABCMeta
    pass
