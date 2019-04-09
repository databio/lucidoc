""" Tests for responsiveness to different modes of target subset specfication """

import glob
import itertools
import os
import random
import string
import sys
import pytest
from lucidoc import run_lucidoc
from lucidoc.docparse import PARSERS


__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


CLS1 = "DummyClass"
CLS2 = "Random"
CLS3 = "Arbitrary"
CLASS_NAMES = [CLS1, CLS2, CLS3]


LINES = """
__author__ = "Vince Reuter"
__all__ = [{cs}]

class {c1}(object):
    
    def fun1(self):
        pass
    
    def fun2(self):
        pass


class {c2}(object):
    pass


class {c3}(object):
    pass
""".format(cs=", ".join("\"{}\"".format(n) for n in CLASS_NAMES),
           c1=CLS1, c2=CLS2, c3=CLS3).splitlines(False)


class TmpPathContext(object):
    """ Temporarily alter the state of sys.path. """

    def __init__(self, p):
        self.p = p

    def __enter__(self):
        assert self.p not in sys.path, "Already on sys.path: {}".format(self.p)
        sys.path.append(self.p)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.path = [p for p in sys.path if p != self.p]


@pytest.fixture
def target_package(request, tmpdir):
    """
    Write dummy python module and return path to corresponding file.

    :param pytest.fixtures.FixtureRequest request: test case requesting
        parameterization
    :param py.path.local.LocalPath tmpdir: temporary folder for a test case
    :return str: path to the dummy Python module written
    """
    lines = request.getfixturevalue("lines") \
        if "lines" in request.fixturenames else LINES
    pkg = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    pkg_dir = os.path.join(tmpdir.strpath, pkg)
    os.makedirs(pkg_dir)
    fn = "".join(random.choice(string.ascii_letters) for _ in range(15)) + ".py"
    # DEBUG
    print("LINES:\n" + "\n".join(lines))
    with open(os.path.join(pkg_dir, fn), 'w') as f:
        f.write("\n".join(lines))
    with open(os.path.join(pkg_dir, "__init__.py"), 'w'):
        return pkg


def pytest_generate_tests(metafunc):
    """ Module-level test case parameterization """
    # Tests should hold regardless of parser style.
    metafunc.parametrize("parse_style", PARSERS.keys())


@pytest.mark.parametrize("whitelist",
    list(itertools.chain(*[itertools.combinations(CLASS_NAMES, k)
                           for k in range(1, 1 + len(CLASS_NAMES))])))
def test_whitelist_sensitivity(parse_style, target_package, whitelist, tmpdir):
    """ Any available whitelisted entity should be used/included. """
    fn = "".join(random.choice(string.ascii_letters) for _ in range(15)) + ".md"
    outfile = tmpdir.join(fn).strpath
    with TmpPathContext(tmpdir.strpath):
        run_lucidoc(target_package, parse_style=parse_style,
                    outfile=outfile, whitelist=whitelist)
    with open(outfile, 'r') as f:
        contents = f.read()
    goods = set(whitelist)
    bads = set(CLASS_NAMES) - goods
    missing = [n for n in goods if n not in contents]
    present = [n for n in bads if n in contents]
    # DEBUG
    print("FILES:\n" + "\n".join(os.listdir(os.path.join(tmpdir.strpath, target_package))))
    mods = [f for f in glob.glob(os.path.join(tmpdir.strpath, target_package, "*.py")) if not f.endswith("__init__.py")]
    print("MODS: {}".format(mods))
    with open(mods[0], 'r') as f:
        print("MODULE:\n" + f.read())
    print("CONTENTS:\n" + contents)
    assert [] == missing, \
        "Missing {} doc target(s):\n{}".format(len(missing), "\n".join(missing))
    assert [] == present, \
        "{} unexpected doc target(s):\n{}".format(len(present), "\n".join(present))


@pytest.mark.skip("Not implemented")
def test_whitelist_specificity(parse_style):
    """ Non whitelisted entities should be excluded. """
    pass


@pytest.mark.skip("Not implemented")
def test_blacklist_sensitivity(parse_style):
    """ Any blacklisted entity should be excluded. """
    pass


@pytest.mark.skip("Not implemented")
def test_blacklist_specificity(parse_style):
    """ Available, non-blacklisted entities should be used/included. """
    pass
