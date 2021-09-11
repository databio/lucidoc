""" Tests for parsing the non-tag sections of a docstring """

import pytest
import lucidoc
from lucidoc.docparse import RST_EXAMPLE_TAG
from tests.conftest import build_args_space, CODE_EX1, DESC_KEY, \
    EXS_KEY, HEADLINE, DETAIL_LINES, LONG_DESC_KEY, SHORT_DESC_KEY
from ubiquerg import powerset

__author__ = "Vince Reuter"


@pytest.mark.parametrize("blank_line_sep", [False, True])
@pytest.mark.parametrize("pool", build_args_space(
    allow_empty=False,
    **{EXS_KEY: [{EXS_KEY: items} for items in powerset([CODE_EX1], nonempty=True)]}))
def test_examples(pool, ds_spec, blank_line_sep):
    """ Check that number of example blocks parsed is as expected. """
    parser = lucidoc.RstDocstringParser()
    # Hack for post-hoc modification of specification fixture
    blank_space_param = "space_between_examples"
    setattr(ds_spec, blank_space_param, blank_line_sep)
    ds = ds_spec.render()
    exs = parser.examples(ds)
    num_ex_exp = ds.count(RST_EXAMPLE_TAG)
    num_ex_obs = sum(1 for _ in
        filter(lambda s: s.startswith("```") and not s.strip() == "```", exs))
    assert num_ex_exp == num_ex_obs, \
        "{} example(s) and {} example tag(s)\nExamples chunks: {}".\
            format(num_ex_obs, num_ex_exp, exs)
    # TODO: verify parsed CONTENT relative to input, rather than simply block count.


@pytest.mark.skip("Not implemented")
@pytest.mark.parametrize("pool",
    build_args_space(allow_empty=True,
        **{DESC_KEY: [{SHORT_DESC_KEY: h, LONG_DESC_KEY: d} for h, d in
                      [(HEADLINE, None), (None, DETAIL_LINES),
                      (HEADLINE, DETAIL_LINES)]]}
    ))
def test_description(pool, ds_spec, parser):
    """ Test proper parsing of short and/or long description. """
    pass
