""" Tests for parsing and rendering docstrings that span multiple lines. """

import pytest
import oradocle

from conftest import DESC_KEY, PAR_KEY, RET_KEY, ERR_KEY, EXS_KEY, DESC_POOL, \
    PARAM_POOL, RETURN_POOL, ERROR_POOL, CODE_POOL, SPACE_POOL, \
    RETURN, RETURN_MUTLI_LINE, build_args_space

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


@pytest.mark.parametrize("pool",
    build_args_space(
        allow_empty=False, **{PAR_KEY: None, RET_KEY: None, ERR_KEY: None}))
def test_no_tags(pool, ds_spec, parser):
    """ When no tags are present, none are parsed. """
    # DEBUG
    print("POOL:\n{}\n".format(
        "\n".join("{}: {}".format(k, v) for k, v in pool.items())))
    ds = ds_spec.render()
    print("DS:\n{}".format(ds))
    assert_exp_line_count(ds, ds_spec)
    assert_exp_tag_count(ds, ds_spec, parser)


@pytest.mark.parametrize("pool",
    build_args_space(allow_empty=False,
        **{DESC_KEY: None, RET_KEY: None, ERR_KEY: None, EXS_KEY: None}))
def test_only_params(pool, ds_spec, parser):
    """ When only return tag is present, it's used. """
    # DEBUG
    print("POOL:\n{}\n".format(
        "\n".join("{}: {}".format(k, v) for k, v in pool.items())))
    ds = ds_spec.render()
    print("DS:\n{}".format(ds))
    assert_exp_line_count(ds, ds_spec)
    assert_exp_tag_count(ds, ds_spec, parser)
    desc = parser.description(ds)
    assert desc is None or (desc == "")
    ret = parser.returns(ds)
    assert ret is None or (ret == [])
    err = parser.raises(ds)
    assert [] == err
    par = parser.params(ds)
    assert len(par) == len(pool[PAR_KEY])
    assert all(isinstance(t, oradocle.ParTag) for t in par)


@pytest.mark.parametrize("pool", build_args_space(allow_empty=False,
    **{DESC_KEY: None, PAR_KEY: None, ERR_KEY: None, EXS_KEY: None}))
def test_only_returns(pool, ds_spec, parser):
    """ When only return tag is present, it's used. """
    # DEBUG
    print("POOL:\n{}\n".format(
        "\n".join("{}: {}".format(k, v) for k, v in pool.items())))
    ds = ds_spec.render()
    print("DS:\n{}".format(ds))
    assert_exp_line_count(ds, ds_spec)
    assert_exp_tag_count(ds, ds_spec, parser)


@pytest.mark.parametrize("pool", build_args_space(
    allow_empty=False, **{RET_KEY: [{RET_KEY: [RETURN, RETURN_MUTLI_LINE]}]}))
def test_multiple_returns(pool, ds_spec, parser):
    """ Multiple return tags are prohibited. """
    ds = ds_spec.render()
    # DEBUG
    print("POOL:\n{}\n".format(
        "\n".join("{}: {}".format(k, v) for k, v in pool.items())))
    print("DS:\n{}".format(ds))
    with pytest.raises(oradocle.OradocError):
        parser._parse(ds)


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
    assert ds.count("\n") == spec.exp_line_count


def assert_exp_tag_count(ds, spec, parser):
    """ Assert that number of parsed tags is as expected. """
    # DEBUG
    print("PARAMS: {}".format(parser.params(ds)))
    rets = parser.returns(ds)
    rets = rets or []
    if isinstance(rets, oradocle.RetTag):
        rets = [rets]
    tags = parser.params(ds) + rets + parser.raises(ds)
    print("TAGS:\n{}".format("\n".join(str(t) for t in tags)))
    assert len(tags) == spec.exp_tag_count, "All tag texts ({}):\n{}".format(len(spec.all_tag_texts), "\n".join(spec.all_tag_texts))
