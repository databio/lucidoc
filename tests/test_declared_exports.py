""" Tests for usage of declared exports vs. all members """

import itertools
import os
import pytest
from lucidoc.docparse import PARSERS
from tests.conftest import CLASS_NAMES, TEMP_CLS_1, TEMP_CLS_2, \
    TEMP_CLS_3
from tests.helpers import exec_test, make_exports_declaration

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


EXPORTS_KEY = "exports"

MODLINES = """
__author__ = "Vince Reuter"

class {c1}(object):

    def fun1(self):
        pass

    def fun2(self):
        pass


class {c2}(object):
    pass


class {c3}(object):
    pass
""".format(c1=TEMP_CLS_1, c2=TEMP_CLS_2, c3=TEMP_CLS_3).splitlines(False)


def pytest_generate_tests(metafunc):
    """ Module-level test case parameterization """
    if EXPORTS_KEY in metafunc.fixturenames:
        metafunc.parametrize(EXPORTS_KEY, list(itertools.chain(*[
            itertools.combinations(CLASS_NAMES, k) 
            for k in range(1, 1 + len(CLASS_NAMES))])))
    # Tests should hold regardless of parser style.
    metafunc.parametrize("parse_style", PARSERS.keys())


@pytest.fixture
def modlines(request):
    """ Lines to write as temp module file for a test case """
    return [MODLINES[0]] + \
           [make_exports_declaration(request.getfixturevalue(EXPORTS_KEY))] + \
           MODLINES[1:] if EXPORTS_KEY in request.fixturenames else MODLINES


def test_export_sensitivity(
        tmpdir, target_package, parse_style, exports, modlines):
    """ Each exported member is documented. """
    try_cat_module(os.path.join(tmpdir.strpath, target_package))
    contents = exec_test(tmpdir.strpath, target_package, parse_style)
    missing = [n for n in exports if n not in contents]
    assert [] == missing, \
        "Missing {} doc target(s):\n{}".format(len(missing), "\n".join(missing))


def test_export_specificifty(
        tmpdir, target_package, parse_style, exports, modlines):
    """ When exports are declared, only those members are documented. """
    try_cat_module(os.path.join(tmpdir.strpath, target_package))
    contents = exec_test(tmpdir.strpath, target_package, parse_style)
    present = [n for n in set(CLASS_NAMES) - set(exports) if n in contents]
    assert [] == present, \
        "{} unexpected doc target(s):\n{}".format(len(present), "\n".join(present))


def try_cat_module(folder):
    mods = [os.path.join(folder, f) for f in os.listdir(folder)
            if f.endswith(".py") and f != "__init__.py"]
    if len(mods) == 1:
        with open(mods[0], 'r') as f:
            print("Contents of module {} from folder {}:\n{}".format(
                mods[0], folder, f.read()))
    else:
        print("Not printing module contents; did not find exactly 1 module in "
              "folder {}: {}".format(folder, mods))
