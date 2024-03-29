""" Tests for parsing and rendering docstrings that span multiple lines. """

import pytest
import lucidoc
from tests.conftest import (
    DESC_KEY,
    PAR_KEY,
    RET_KEY,
    ERR_KEY,
    EXS_KEY,
    TYPE_ERROR,
    VALUE_ERROR,
    RETURN,
    RETURN_MUTLI_LINE,
    build_args_space,
)
from ubiquerg import powerset

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


def pytest_generate_tests(metafunc):
    if "exclude_tag_type" in metafunc.fixturenames:
        metafunc.parametrize(
            ["exclude_tag_type", "pool"],
            [
                (xtt, p)
                for xtt in [PAR_KEY, RET_KEY, ERR_KEY]
                for p in build_args_space(allow_empty=False, **{xtt: None})
            ],
        )


@pytest.mark.parametrize(
    "pool",
    build_args_space(
        allow_empty=False, **{PAR_KEY: None, RET_KEY: None, ERR_KEY: None}
    ),
)
def test_no_tags(pool, ds_spec, parser):
    """When no tags are present, none are parsed."""
    ds = ds_spec.render()
    assert_exp_line_count(ds, ds_spec)
    assert_exp_tag_count(ds, ds_spec, parser)


@pytest.mark.parametrize(
    "pool",
    build_args_space(
        allow_empty=False,
        **{DESC_KEY: None, RET_KEY: None, ERR_KEY: None, EXS_KEY: None}
    ),
)
def test_only_params(pool, ds_spec, parser):
    """When only return tag is present, it's used."""
    ds = ds_spec.render()
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
    assert all(isinstance(t, lucidoc.ParTag) for t in par)


@pytest.mark.parametrize(
    "pool",
    build_args_space(
        allow_empty=False,
        **{DESC_KEY: None, PAR_KEY: None, ERR_KEY: None, EXS_KEY: None}
    ),
)
def test_only_returns(pool, ds_spec, parser):
    """When only return tag is present, it's used."""
    ds = ds_spec.render()
    assert_exp_line_count(ds, ds_spec)
    assert_exp_tag_count(ds, ds_spec, parser)


@pytest.mark.parametrize(
    "pool",
    build_args_space(
        allow_empty=False,
        **{DESC_KEY: None, PAR_KEY: None, RET_KEY: None, EXS_KEY: None}
    ),
)
def test_only_raises(pool, ds_spec, parser):
    ds = ds_spec.render()
    assert_exp_line_count(ds, ds_spec)
    assert_exp_tag_count(ds, ds_spec, parser)
    desc = parser.description(ds)
    assert desc is None or (desc == "")
    ret = parser.returns(ds)
    assert ret is None or (ret == [])
    err = parser.raises(ds)
    assert [] == parser.params(ds)
    assert len(err) > 0
    assert len(err) == len(pool[ERR_KEY])
    assert all(isinstance(t, lucidoc.ErrTag) for t in err)


def test_specific_tag_type_omission(exclude_tag_type, pool, ds_spec, parser):
    ds = ds_spec.render()
    assert_exp_line_count(ds, ds_spec)
    assert_exp_tag_count(ds, ds_spec, parser)
    assert [] == (getattr(parser, exclude_tag_type)(ds) or [])


@pytest.mark.parametrize("tag", [":return", ":returns"])
@pytest.mark.parametrize(
    "pool",
    build_args_space(
        allow_empty=False,
        **{RET_KEY: [{RET_KEY: [RETURN]}, {RET_KEY: [RETURN_MUTLI_LINE]}]}
    ),
)
def test_return_vs_returns(tag, pool, ds_spec):
    """Both styles of result docstring are allowed."""
    ds1 = ds_spec.render()
    parser = lucidoc.RstDocstringParser()
    ret1 = parser.returns(ds1)
    ds2 = ds1.replace(":return", tag).replace(":returns", tag)
    ret2 = parser.returns(ds2)
    assert isinstance(ret1, lucidoc.RetTag)
    assert isinstance(ret2, lucidoc.RetTag)
    assert ret1.typename == ret2.typename
    assert ret1.description == ret2.description


@pytest.mark.parametrize("tag", [":raise", ":raises"])
@pytest.mark.parametrize(
    "pool",
    build_args_space(
        allow_empty=False,
        **{
            ERR_KEY: [
                {ERR_KEY: items}
                for items in powerset([VALUE_ERROR, TYPE_ERROR], nonempty=True)
            ]
        }
    ),
)
def test_raise_vs_raises(tag, pool, ds_spec):
    """Both styles of exception docstring are allowed."""
    ds1 = ds_spec.render()
    parser = lucidoc.RstDocstringParser()
    err1 = parser.raises(ds1)
    ds2 = ds1.replace(":raise", tag).replace(":raises", tag)
    err2 = parser.raises(ds2)
    assert len(err1) > 0
    assert len(err1) == len(err2)
    assert all(isinstance(e, lucidoc.ErrTag) for e in err1)
    assert all(isinstance(e, lucidoc.ErrTag) for e in err2)
    assert all(e1.typename == e2.typename for e1, e2 in zip(err1, err2))
    assert all(e1.description == e2.description for e1, e2 in zip(err1, err2))


@pytest.mark.parametrize(
    "pool",
    build_args_space(
        allow_empty=False, **{RET_KEY: [{RET_KEY: [RETURN, RETURN_MUTLI_LINE]}]}
    ),
)
def test_multiple_returns(pool, ds_spec, parser):
    """Multiple return tags are prohibited."""
    ds = ds_spec.render()
    with pytest.raises(lucidoc.LucidocError):
        parser._parse(ds)


def assert_exp_line_count(ds, spec):
    """
    Check that docstring's apparent line count matches expectation.

    :param str ds: docstring to check
    :param lucidoc.tests.DocstringSpecification spec: parameterization and
        expectations for docstring
    """
    assert ds.count("\n") == spec.exp_line_count


def assert_exp_tag_count(ds, spec, parser):
    """
    Assert that number of parsed tags is as expected.

    :param str ds: docstring to check
    :param lucidoc.tests.DocstringSpecification spec: parameterization and
        expectations for docstring
    :param lucidoc.DocstringParser: object with which to parse docstring
    """
    rets = parser.returns(ds)
    rets = rets or []
    if isinstance(rets, lucidoc.RetTag):
        rets = [rets]
    tags = parser.params(ds) + rets + parser.raises(ds)
    assert len(tags) == spec.exp_tag_count, "All tag texts ({}):\n{}".format(
        len(spec.all_tag_texts), "\n".join(spec.all_tag_texts)
    )
