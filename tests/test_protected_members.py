""" Tests for handling of protected module/class members """

import itertools
import os
import random
import string
from lucidoc.docparse import PARSERS
from tests.helpers import exec_test, powerset
import pytest

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


CLS1 = "RandomClass1"
CLS2 = "DummyClass"
CLS3 = "RandomClass2"
FUN1 = "fun1"
FUN2 = "fun2"
FUN3 = "func3"
FUN4 = "func4"
STATIC_METHOD = "fA"
PROPERTY = "prop"


MODLINES_TEMPLATE = """
__author__ = "Vince Reuter"


class {c1}(object):

    def {f1}(self):
        pass

    def {f2}(self):
        pass


class {c2}(object):
    pass
     

class {c3}(object):
    
    @staticmethod
    def {statfun}():
        pass
        
    @property
    def {prop}(self):
        pass

def {f3}():
    pass
    
    
def {f4}():
    pass

"""


NESTING = {"c1": ["f1", "f2"], "c3": ["statfun", "prop"]}
DATA = {"c1": CLS1, "f1": FUN1, "f2": FUN2, "f3": FUN3, "f4": FUN4,
        "c2": CLS2, "c3": CLS3, "statfun": STATIC_METHOD, "prop": PROPERTY}


def pytest_generate_tests(metafunc):
    """ Module-level test case parameterization """
    if "protected" in metafunc.fixturenames:
        metafunc.parametrize("protected", powerset(DATA.keys()))
    # Tests should hold regardless of parser style.
    metafunc.parametrize("parse_style", PARSERS.keys())


@pytest.fixture
def modlines(request):
    """ Provide test case with lines for module in package to doc. """
    protected = request.getfixturevalue("protected")
    data = {k: "_" + v if k in protected else v for k, v in DATA.items()}
    return MODLINES_TEMPLATE.format(**data).splitlines(False)


@pytest.fixture
def target_package(request, tmpdir):
    """
    Write dummy python module and return path to corresponding file.

    :param pytest.fixtures.FixtureRequest request: test case requesting
        parameterization
    :param py.path.local.LocalPath tmpdir: temporary folder for a test case
    :return str: path to the dummy Python module written
    """
    lines = request.getfixturevalue("modlines")
    pkg = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    pkg_dir = os.path.join(tmpdir.strpath, pkg)
    os.makedirs(pkg_dir)
    file_name_base = "".join(
        random.choice(string.ascii_letters) for _ in range(15))
    filename = file_name_base + ".py"
    assert [] == [f for f in os.listdir(pkg_dir) if f.endswith(".pyc")]
    with open(os.path.join(pkg_dir, filename), 'w') as f:
        f.write("\n".join(lines))
    init_lines = ["from .{} import *".format(file_name_base)]
    with open(os.path.join(pkg_dir, "__init__.py"), 'w') as f:
        f.write("\n\n".join(init_lines))
    return pkg


def test_protection_sensitivity(
        tmpdir, target_package, parse_style, protected, modlines):
    """ Protected members are not documented. """
    output = exec_test(tmpdir.strpath, target_package, parse_style)
    exp_absent_names = {n for k in protected for n in
                        [DATA[k]] + [DATA[ksub] for ksub in NESTING.get(k, [])]}
    present = {n for n in exp_absent_names if n in output or "_" + n in output}
    assert set() == present, "{} unexpected doc target(s):\n{}".\
        format(len(present), "\n".join(present))


def test_protection_specificity(
        tmpdir, target_package, parse_style, protected, modlines):
    """ Unprotected members are documented. """
    output = exec_test(tmpdir.strpath, target_package, parse_style)
    prot_keys = set(protected) | \
                set(itertools.chain(*[NESTING.get(k, []) for k in protected]))
    exp_present_names = {v for k, v in DATA.items() if k not in prot_keys}
    missing = {n for n in exp_present_names if n not in output}
    mods = [os.path.join(tmpdir.strpath, target_package, f) for f in
            os.listdir(os.path.join(tmpdir.strpath, target_package))
            if f != "__init__.py" and f.endswith(".py")]
    assert 1 == len(mods)
    with open(mods[0], 'r') as f:
        print("Conents of file {}:\n".format(mods[0]) + f.read())
    assert set() == missing, \
        "Missing {} doc target(s):\n{}".format(len(missing), "\n".join(missing))
