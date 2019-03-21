""" Test suite helpers """

import os
import shutil


__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


class SafeExec(object):
    """ Run something that could erroneously write output; clean it if so. """
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

