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


def _make_exports_declaration(names):
    """
    Create a module's declaration of exported members.

    :param Iterable[str] names: names that should be declared as exports
    :return str: the export declaration specification
    """
    return "__all__ = [{}]".format(", ".join("\"{}\"".format(n) for n in names))


LINES = """
__author__ = "Vince Reuter"
{exports}

class {c1}(object):
    
    def fun1(self):
        pass
    
    def fun2(self):
        pass


class {c2}(object):
    pass


class {c3}(object):
    pass
""".format(exports=_make_exports_declaration(CLASS_NAMES),
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
    file_name_base = "".join(
        random.choice(string.ascii_letters) for _ in range(15))
    filename = file_name_base + ".py"
    # DEBUG
    print("LINES:\n" + "\n".join(lines))
    with open(os.path.join(pkg_dir, filename), 'w') as f:
        f.write("\n".join(lines))
    init_lines = [
        "from {} import *".format(file_name_base),
        _make_exports_declaration(CLASS_NAMES)]
    with open(os.path.join(pkg_dir, "__init__.py"), 'w') as f:
        f.write("\n\n".join(init_lines))
    return pkg


def pytest_generate_tests(metafunc):
    """ Module-level test case parameterization """

    def param_class_names(mf, fix_name):
        if fix_name in mf.fixturenames:
            mf.parametrize(fix_name, list(itertools.chain(*[
                itertools.combinations(CLASS_NAMES, k)
                for k in range(1, 1 + len(CLASS_NAMES))])))

    # Tests should hold regardless of parser style.
    metafunc.parametrize("parse_style", PARSERS.keys())

    param_class_names(metafunc, "whitelist")
    param_class_names(metafunc, "blacklist")


def test_whitelist_sensitivity(parse_style, target_package, whitelist, tmpdir):
    """ Any available whitelisted entity should be used/included. """
    fn = "".join(random.choice(string.ascii_letters) for _ in range(15)) + ".md"
    outfile = tmpdir.join(fn).strpath
    with TmpPathContext(tmpdir.strpath):
        run_lucidoc(target_package, parse_style=parse_style,
                    outfile=outfile, whitelist=whitelist)
    with open(outfile, 'r') as f:
        contents = f.read()
    missing = [n for n in set(whitelist) if n not in contents]
    # DEBUG
    print("Files in package folder:\n" + "\n".join(
        os.listdir(os.path.join(tmpdir.strpath, target_package))))
    print("Outfile contents:\n" + contents)
    assert [] == missing, \
        "Missing {} doc target(s):\n{}".format(len(missing), "\n".join(missing))


def test_whitelist_specificity(parse_style, target_package, whitelist, tmpdir):
    """ Non whitelisted entities should be excluded. """
    fn = "".join(random.choice(string.ascii_letters) for _ in range(15)) + ".md"
    outfile = tmpdir.join(fn).strpath
    with TmpPathContext(tmpdir.strpath):
        run_lucidoc(target_package, parse_style=parse_style,
                    outfile=outfile, whitelist=whitelist)
    with open(outfile, 'r') as f:
        contents = f.read()
    bads = set(CLASS_NAMES) - set(whitelist)
    present = [n for n in bads if n in contents]
    assert [] == present, \
        "{} unexpected doc target(s):\n{}".format(len(present), "\n".join(present))


@pytest.mark.skip("Not implemented")
def test_blacklist_sensitivity(parse_style, target_package, blacklist, tmpdir):
    """ Any blacklisted entity should be excluded. """
    pass


@pytest.mark.skip("Not implemented")
def test_blacklist_specificity(parse_style, target_package, blacklist, tmpdir):
    """ Available, non-blacklisted entities should be used/included. """
    pass
