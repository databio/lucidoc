""" Tests for responsiveness to different modes of target subset specfication """

import pytest
from lucidoc.docparse import PARSERS


__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


def pytest_generate_tests(metafunc):
    """ Module-level test case parameterization """
    # Tests should hold regardless of parser style.
    metafunc.parametrize("parse_style", PARSERS.keys())


@pytest.mark.skip("Not implemented")
def test_whitelist_sensitivity(parse_style):
    pass


@pytest.mark.skip("Not implemented")
def test_whitelist_specificity(parse_style):
    pass


@pytest.mark.skip("Not implemented")
def test_blacklist_sensitivity(parse_style):
    pass


@pytest.mark.skip("Not implemented")
def test_blacklist_sensitivity(parse_style):
    pass
