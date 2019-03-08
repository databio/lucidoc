""" Tests for parsing and rendering docstrings that span multiple lines. """

import itertools
import pytest
import oradocle

from conftest import DESC_POOL, PARAM_POOL, RETURN_POOL, ERROR_POOL, CODE_POOL, \
    SPACE_POOL, build_args_space

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


@pytest.mark.parametrize(
    "pool", build_args_space(params=None, returns=None, raises=None))
def test_no_tags(pool, ds_spec, parser):
    """ When no tags are present, none are parsed. """
    ds = ds_spec.render()
    assert_exp_line_count(ds, ds_spec)
    assert_exp_tag_count(ds, ds_spec, parser)


@pytest.mark.skip("Not implemented")
def test_only_params():
    """ When only return tag is present, it's used. """
    pass


@pytest.mark.skip("Not implemented")
def test_only_returns():
    """ When only return tag is present, it's used. """
    pass


@pytest.mark.skip("Not implemented")
def test_multiple_returns():
    """ Multiple return tags are prohibited. """
    pass


@pytest.mark.skip("Not implemented")
def test_only_raises():
    pass


@pytest.mark.skip("Not implemented")
def test_no_params():
    """ When parameter tags are missing, none are parsed. """
    pass


@pytest.mark.skip("Not implemented")
def test_no_returns():
    """ When returns tag is missing, none is parsed. """
    pass


@pytest.mark.skip("Not implemented")
def test_no_raises():
    """ When exception tags are missing, none are parsed. """
    pass


@pytest.mark.skip("Not implemented")
def test_golden_canonical():
    """ All kinds of tags present, with/out both description sections. """
    pass


@pytest.mark.skip("Not imlpemented")
def test_return_vs_returns():
    """ Both styles of result docstring are allowed. """
    pass


@pytest.mark.skip("Not implemented")
def test_raise_vs_raises():
    """ Both styles of exception docstring are allowed. """
    pass


def assert_exp_line_count(ds, spec):
    assert len(ds.splitlines()) == spec.exp_line_count


def assert_exp_tag_count(ds, spec, parser):
    """ Assert that number of parsed tags is as expected. """
    tags = parser.params(ds) + parser.returns()
    assert len(tags) == spec.exp_tag_count
