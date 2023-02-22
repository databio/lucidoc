""" Test suite helpers """

import itertools
import os
import random
import shutil
import string
import sys
from lucidoc import run_lucidoc


__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


def exec_test(folder, pkg, parse_style, **kwargs):
    """
    Call lucidoc runner and parse the output file's contents.

    :param str folder: path to test's root temp folder
    :param str pkg: name of package to test document
    :param str parse_style: name of the parsing style
    :returns str: output file's contents
    """
    fn = "".join(random.choice(string.ascii_letters) for _ in range(15)) + ".md"
    outfile = os.path.join(folder, fn)
    with TmpTestCtx(folder):
        run_lucidoc(pkg, parse_style, outfile=outfile, **kwargs)
    with open(outfile, "r") as f:
        return f.read()


def make_exports_declaration(names):
    """
    Create a module's declaration of exported members.

    :param Iterable[str] names: names that should be declared as exports
    :return str: the export declaration specification
    """
    return "__all__ = [{}]".format(", ".join('"{}"'.format(n) for n in names))


class SafeExec(object):
    """Run something that could erroneously write output; clean it if so."""

    def __init__(self):
        self.folder = os.getcwd()
        self.original_contents = set(os.listdir(self.folder))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for n in set(os.listdir(self.folder)) - self.original_contents:
            p = os.path.join(self.folder, n)
            if os.path.isfile(p):
                os.unlink(p)
            elif os.path.isdir(p):
                shutil.rmtree(p)


class TmpTestCtx(object):
    """Temporarily alter the state of sys.path."""

    def __init__(self, p):
        self.p = p

    def __enter__(self):
        assert self.p not in sys.path, "Already on sys.path: {}".format(self.p)
        sys.path.append(self.p)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.path = [p for p in sys.path if p != self.p]
