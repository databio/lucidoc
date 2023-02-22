""" Tests for how to specify output """

import abc
import copy
import itertools
import os
import random
import string
import pytest
import lucidoc
from lucidoc import run_lucidoc, LucidocError
from lucidoc import docparse, docstyle
from lucidoc.docparse import PARSERS
from tests.helpers import SafeExec


__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


PARSER_GROUP_NAME = "parser"
STYLER_GROUP_NAME = "styler"
GROUP_NAMES = [PARSER_GROUP_NAME, STYLER_GROUP_NAME]


def run(*args, **kwargs):
    """Call the package's main workflow."""
    kwds = {"pkg": lucidoc.__name__}
    kwds.update(kwargs)
    return run_lucidoc(*args, **kwds)


def pytest_generate_tests(metafunc):
    """Module-level test case parameterization"""
    # Tests should hold regardless of parser style.
    if metafunc.cls != ParseStyleTests:
        metafunc.parametrize("parse_style", PARSERS.keys())


class GroupSpec(object):
    """Specification of the data needed to declare groupings."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, data):
        """
        Create the specification by providing the raw grouping.

        :param Iterable[(str, str | Sequence[str])] data: collection of pairs
            in which first component is group name and second is a single
            member name or a collection of member names
        """
        self._data = data

    @property
    def groups(self):
        return copy.deepcopy(self._data)

    @staticmethod
    def ensure_extension(n):
        return n if n.endswith(".md") else n + ".md"

    @abc.abstractproperty
    def filenames(self):
        """
        Return the filenames expected based on the named groupings.

        :return Iterable[str]: collection in which each element is a filename
            that may be produced if the documentation workflow runs.
        """
        pass


class SeqGroupSpec(GroupSpec):
    """List-backed specification of output groups"""

    def __init__(self, data):
        assert isinstance(
            data, list
        ), "Attempted to specify sequence group with data of type {}".format(type(data))
        super(SeqGroupSpec, self).__init__(data)

    @property
    def filenames(self):
        return [self.ensure_extension(n) for n, _ in self._data]


class MapGroupSpec(GroupSpec):
    """Map-backed specification of output groups"""

    def __init__(self, data):
        super(MapGroupSpec, self).__init__(dict(data))

    @property
    def filenames(self):
        return [self.ensure_extension(n) for n in self._data]


@pytest.fixture(scope="function", params=[SeqGroupSpec, MapGroupSpec])
def spec_type(request):
    """Parameterize over group specification structures."""
    return request.param


@pytest.fixture(scope="function")
def gspec(spec_type):
    """Create a specification of groups of documenatation targets."""
    return spec_type(
        [(STYLER_GROUP_NAME, docstyle.__all__), (PARSER_GROUP_NAME, docparse.__all__)]
    )


def test_only_package_and_style_are_required(parse_style):
    """Validate minimal specification requirement to run the workflow."""
    with pytest.raises(TypeError):
        run_lucidoc(parse_style=parse_style)
    with pytest.raises(TypeError):
        run_lucidoc(lucidoc.__name__)
    try:
        run(parse_style=parse_style)
    except Exception as e:
        pytest.fail(str(e))


@pytest.mark.parametrize(
    "filename", ["".join(random.choice(string.ascii_letters) + ".md")]
)
def test_outfile_outfolder_mutual_exclusivity(parse_style, tmpdir, filename):
    """Outfile is a single filepath; outfolder is for multiple paths."""
    folder = tmpdir.strpath
    fp = os.path.join(folder, filename)
    with pytest.raises(LucidocError):
        run(parse_style=parse_style, outfile=fp, outfolder=folder)


def test_groups_without_outfolder_uses_cwd(gspec, parse_style):
    """Grouped output is distributed to different files, requiring folder."""
    files = [os.path.join(os.getcwd(), fn) for fn in gspec.filenames]
    assert not any([os.path.exists(f) for f in files])
    with SafeExec():
        run(parse_style=parse_style, groups=gspec.groups)
        print("GROUPS: {}".format(gspec.groups))
        assert all([os.path.isfile(f) for f in files])


def test_groups_preclude_outfile(parse_style, tmpdir, gspec):
    """Single output file makes no sense in context of output groups."""
    f = tmpdir.join("".join(random.choice(string.ascii_letters)) + ".md").strpath
    with pytest.raises(LucidocError), SafeExec():
        run(parse_style=parse_style, outfile=f, groups=gspec.groups)


@pytest.mark.parametrize(
    "extra_kwargs",
    [
        {listname: groups}
        for listname, groups in itertools.product(
            ["blacklist", "whitelist"],
            [
                list(ns)
                for ns in itertools.chain(
                    *[
                        list(itertools.combinations(GROUP_NAMES, k))
                        for k in range(1, len(GROUP_NAMES) + 1)
                    ]
                )
            ],
        )
    ],
)
def test_groups_precluse_whitelist_or_blacklist(parse_style, gspec, extra_kwargs):
    """Groups spec implies whitelist and cannot be used with other lists."""
    with pytest.raises(LucidocError), SafeExec():
        run(parse_style=parse_style, groups=gspec.groups, **extra_kwargs)


@pytest.mark.parametrize(
    "extra_kwargs",
    [
        {"blacklist": PARSER_GROUP_NAME, "whitelist": STYLER_GROUP_NAME},
        {"blacklist": STYLER_GROUP_NAME, "whitelist": PARSER_GROUP_NAME},
    ],
)
def test_whitelist_with_blacklist_is_prohibited(parse_style, extra_kwargs):
    with pytest.raises(LucidocError), SafeExec():
        run(parse_style=parse_style, **extra_kwargs)


class ParseStyleTests:
    """Smoketests related to parser style"""

    @staticmethod
    @pytest.mark.parametrize("style", ["not_a_valid_style", "invalid_style_2"])
    def test_unrecognized_parser_style_is_exceptional(style):
        with pytest.raises(LucidocError):
            run(parse_style=style)
