""" Custom exception types """

import abc


class OradocleError(Exception):
    """ Base error type for this package """
    __metaclass__ = abc.ABCMeta
    pass
