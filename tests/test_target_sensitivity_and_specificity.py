""" Tests for responsiveness to different modes of target subset specfication """

import itertools
import os
from lucidoc.docparse import PARSERS
from tests.conftest import CLASS_NAMES
from tests.helpers import exec_test


__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


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
    contents = exec_test(
        tmpdir.strpath, target_package, parse_style, whitelist=whitelist)
    missing = [n for n in set(whitelist) if n not in contents]
    # DEBUG
    print("Files in package folder:\n" + "\n".join(
        os.listdir(os.path.join(tmpdir.strpath, target_package))))
    print("Outfile contents:\n" + contents)
    assert [] == missing, \
        "Missing {} doc target(s):\n{}".format(len(missing), "\n".join(missing))


def test_whitelist_specificity(parse_style, target_package, whitelist, tmpdir):
    """ Non whitelisted entities should be excluded. """
    contents = exec_test(
        tmpdir.strpath, target_package, parse_style, whitelist=whitelist)
    bads = set(CLASS_NAMES) - set(whitelist)
    present = [n for n in bads if n in contents]
    assert [] == present, \
        "{} unexpected doc target(s):\n{}".format(len(present), "\n".join(present))


def test_blacklist_sensitivity(parse_style, target_package, blacklist, tmpdir):
    """ Any blacklisted entity should be excluded. """
    contents = exec_test(
        tmpdir.strpath, target_package, parse_style, blacklist=blacklist)
    bads = set(blacklist)
    present = [n for n in bads if n in contents]
    assert [] == present, \
        "{} unexpected doc target(s):\n{}".format(len(present), "\n".join(present))


def test_blacklist_specificity(parse_style, target_package, blacklist, tmpdir):
    """ Available, non-blacklisted entities should be used/included. """
    contents = exec_test(
        tmpdir.strpath, target_package, parse_style, blacklist=blacklist)
    goods = set(CLASS_NAMES) - set(blacklist)
    missing = [n for n in goods if n not in contents]
    assert [] == missing, \
        "{} missing doc target(s):\n{}".format(len(missing), "\n".join(missing))
