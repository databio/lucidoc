""" Output write handling """

import abc
import os
import sys
if sys.version_info < (3, 3):
    from collections import Iterable, Mapping
else:
    from collections.abc import Iterable, Mapping
from .exceptions import LucidocError
from .helpers import expandpath


__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


DEFAULT_EXTENSION = ".md"
VALID_EXTENSIONS = [".md"]


class Writer(object):
    """ How to write output. """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class SingleWriter(Writer):

    def __init__(self, output):
        """
        Create the writer instance with an output name, filename, or filepath.

        :param str output: filename, filepath, or simple name for output;
            if filename, the output is placed in the active directory; if just
            a plain name, an extension is added and that result is treated as
            filename
        """
        super(Writer, self).__init__()
        self._outpath = expandpath(self._finalize_output_path(output))

    def __call__(self, doc, *args, **kwargs):
        folder = os.path.dirname(self._outpath)
        if not os.path.isdir(folder) and folder not in ["", "."]:
            os.makedirs(folder)
        with open(self._outpath, 'w') as f:
            f.write(doc)

    def _finalize_output_path(self, p):
        base, raw_ext = os.path.splitext(p)
        ext = raw_ext or DEFAULT_EXTENSION
        if ext not in VALID_EXTENSIONS:
            raise LucidocError(
                "Invalid extension: {} (from {}); valid extensions: {}".
                format(raw_ext, p, ", ".join(VALID_EXTENSIONS)))
        return base + ext


class GroupedOutput(Writer):
    """ Documentation context in which targets are grouped by output """

    def __init__(self, group_names, folder=None):
        """
        Create a grouped context by provision of the grouping definition.

        :param Iterable[(str, str | Iterable[str])] | Mapping[str, str | Iterable[str]] names_by_outpath:
            the names of the target(s) for documentation, keyed on or paired with the name
            for the documentation output file
        """
        self._folder = folder
        self._group_names = group_names

    def _create_writer(self, name):
        d, fn = os.path.split(name)
        if d in [".", ""]:
            fn +=
        name_base, ext = os.path.splitext(fn)
        if ext in []:

    def __call__(self, docs, *args, **kwargs):
        """

        :param Iterable[(str, str | Iterable[str])] | Mapping[str, str | Iterable[str]] docs:
        :param args:
        :param kwargs:
        :return:
        """
        if isinstance(docs, Mapping)

    @staticmethod
    def _finalize_extension(ext):
        ext = ext or ".md"
        if ext[0] not in ["-", "_", "."]:
            raise LucidocError("Invalid extension {}")
        return ext
