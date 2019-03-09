""" Tests for parsing the non-tag sections of a docstring """

import pytest
import oradocle
from conftest import build_args_space, powerset, CODE_EX1, CODE_EX2, DESC_KEY, \
    EXS_KEY, HEADLINE, DETAIL_LINES, LONG_DESC_KEY, SHORT_DESC_KEY

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"



@pytest.mark.skip("Not implemented")
@pytest.mark.parametrize("blank_line_sep", [False, True])
@pytest.mark.parametrize("pool", build_args_space(
    allow_empty=False,
    **{EXS_KEY: [{EXS_KEY: items} for items in
                 powerset([CODE_EX1, CODE_EX2], nonempty=True)]}
))
def test_examples(pool, ds_spec, blank_line_sep):
    """ Check that number of example blocks parsed is as expected. """
    parser = oradocle.RstDocstringParser()
    blank_space_param = "space_between_examples"
    assert hasattr(parser, blank_space_param)
    setattr(parser, blank_space_param, blank_line_sep)
    ds = ds_spec.render()
    # DEBUG
    print("POOL:\n{}\n".format(
        "\n".join("{}: {}".format(k, v) for k, v in pool.items())))
    print("DS:\n{}".format(ds))
    ex = parser.example(ds)
    assert ex in ds


@pytest.mark.skip("Not implemented")
@pytest.mark.parametrize("pool",
    build_args_space(allow_empty=True,
        **{DESC_KEY: [{SHORT_DESC_KEY: h, LONG_DESC_KEY: d} for h, d in
                      (HEADLINE, None), (None, DETAIL_LINES),
                      (HEADLINE, DETAIL_LINES)]}
    ))
def test_description(pool, ds_spec, parser):
    """ Test proper parsing of short and/or long description. """
    pass
