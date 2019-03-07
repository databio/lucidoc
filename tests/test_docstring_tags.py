""" Tests for parsing and rendering docstrings that span multiple lines. """

import pytest
import oradocle

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


HEADLINE = "This is a short description."
DETAIL_LINES = ["This description provides more detail",
                "split over multiple lines.",
                "It may or may not have intervening or flanking blank line(s)."]


@pytest.fixture(scope="function")
def headline():
    return HEADLINE


@pytest.fixture(scope="function")
def detail_lines():
    return DETAIL_LINES


BOOL_PARAM = ":param bool flag: "
FUNC_PARAM = ":param function(int, int) -> float"
ITER_PARAM = ":param Iterable[Mapping[str, function(Iterable[float]) -> float]]"
UNION_PARAM = ":param str | Iterable[str]"


@pytest.mark.skip("Not implemented")
@pytest.mark.parametrize("parts", [])
def test_no_tags():
    """ When no tags are present, none are parsed. """
    pass


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
