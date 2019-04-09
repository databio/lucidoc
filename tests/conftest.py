""" Package-level test data and fixtures """

from collections import OrderedDict
import itertools
import sys
if sys.version_info < (3, 3):
    from collections import Iterable
else:
    from collections.abc import Iterable
import pytest
from lucidoc.docparse import RST_EXAMPLE_TAG, RstDocstringParser

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


HEADLINE = "This is a short description."
DETAIL_LINES = ["This description provides more detail",
                "split over multiple lines.",
                "It may or may not have intervening or flanking blank line(s)."]

BOOL_PARAM = ":param bool flag: this quickly describes a flag"
FUNC_PARAM = ":param function(int, int) -> float func: this maps two ints to a float"
ITER_PARAM = """:param Iterable[Mapping[str, function(Iterable[float]) -> float]] func_maps: 
    this is a longer description, with too much content to be described on just 
    one line.""".splitlines(False)
UNION_PARAM = ":param str | Iterable[str] env: environment variables to try"

RETURN = ":return int: simple return code"
RETURN_MUTLI_LINE = """:return str: this is a 
    multiline return comment""".splitlines(False)
VALUE_ERROR = ":raise ValueError: if given an invalid particular arg val."
TYPE_ERROR = """:raise TypeError: if one of the given arguments 
    is of an unacceptable type
""".splitlines(False)

CODE_EX1 = """{ex_tag}

.. code-block:: python

    from a import b
    c = 3
""".format(ex_tag=RST_EXAMPLE_TAG).splitlines(False)

CODE_EX2 = """{ex_tag}

.. code-block:: python

    text = "this is the second example"
    text += " and should parse separately from the first"
""".format(ex_tag=RST_EXAMPLE_TAG).splitlines(False)


def powerset(items, nonempty=False):
    """
    Powerset of a collection, optionally excluding the empty set.

    :param items:
    :param nonempty:
    :return:
    """
    return [x for k in range(1 if nonempty else 0, 1 + len(items)) for x in
            itertools.combinations(items, k)]


SHORT_DESC_KEY = "headline"
LONG_DESC_KEY = "detail"
DESC_KEY = "description"
PAR_KEY = "params"
RET_KEY = "returns"
ERR_KEY = "raises"
EXS_KEY = "examples"


DESC_POOL = [{SHORT_DESC_KEY: h, LONG_DESC_KEY: d} for h, d in [
    (None, None), (HEADLINE, None), (None, DETAIL_LINES), (HEADLINE, DETAIL_LINES)
]]
PARAM_POOL = [{PAR_KEY: items} for items in
              powerset([BOOL_PARAM, FUNC_PARAM, ITER_PARAM, UNION_PARAM])]
RETURN_POOL = [{RET_KEY: items} for items in [RETURN, RETURN_MUTLI_LINE]]
ERROR_POOL = [{ERR_KEY: items} for items in powerset([VALUE_ERROR, TYPE_ERROR])]
CODE_POOL = [{EXS_KEY: items} for items in powerset([CODE_EX1, CODE_EX2])]
SPACE_POOL = [dict(zip(
    ("pre_tags_space", "trailing_space"), flags))
    for flags in itertools.product([False, True], [False, True])
]


def build_args_space(allow_empty, **kwargs):
    """
    Create collection of docstring specification parameter schemes.

    :param bool allow_empty: Whether an empty scheme (no parameters) is valid.
    :param kwargs: hook for direct specification for specific tag type(s) of
        pool(s) of argument values from which combinations may be generated
    :return list[dict[str, object]]: collection of mappings from tag type name
        to value
    """

    space_key = "spaces"

    defaults = OrderedDict([
        (DESC_KEY, DESC_POOL), (PAR_KEY, PARAM_POOL), (RET_KEY, RETURN_POOL),
        (ERR_KEY, ERROR_POOL), (EXS_KEY, CODE_POOL), (space_key, SPACE_POOL)
    ])

    def finalize(obj):
        # Homogenize types.
        return obj or [{}]

    def get_pool(name):
        # Fall back to default if nothing is provided.
        # Don't just use kwargs.get(name) or default[name] since the
        # name may be passed explicitly mapping to None, and then default
        # shouldn't be used.
        try:
            return finalize(kwargs[name])
        except KeyError:
            return defaults[name]

    def combine_mappings(ms):
        # Fold (disjoint) key-value maps into one.
        res = {}
        for m in ms:
            for k, v in m.items():
                if k in res:
                    raise ValueError("Duplicate key: {}".format(k))
                res[k] = v
        return res

    # Create and return the space, removing an empty specifications if desired.
    space = [combine_mappings(ps) for ps in
             itertools.product(*[get_pool(n) for n in defaults])]
    if allow_empty:
        return space
    else:
        def nonempty(m):
            return any(filter(lambda v: not isinstance(v, bool), m.values()))
        return list(filter(nonempty, space))


def pytest_generate_tests(metafunc):
    """ Provide test cases with a docstring parser if requested. """
    parser_param_hook = "parser"
    if parser_param_hook in metafunc.fixturenames:
        metafunc.parametrize(parser_param_hook, [RstDocstringParser()])


@pytest.fixture(scope="function")
def ds_spec(request):
    """
    Build a docstring specification.

    The test case itself should already be set in terms of the space of
    docstring specification parameters chose (i.e., the test function
    is parameterized with respect to the available param pools). This fixture
    then simply handles the creation of the docstring specification, from
    which a docstring to parse will be rendered, and which provides the
    expectations against which to perform assertions about the parse result.

    :return lucidoc.tests.DocstringSpecification: a docstring specification
        corresponding to the parameter pool supplied by the test case making
        the request
    """
    pks = ["pool", "excl_pool"]
    for pk in pks:
        if pk in request.fixturenames:
            pool = request.getfixturevalue(pk)
            kwargs = {k: v or None for k, v in pool.items()}
            return DocstringSpecification(**kwargs)
    raise Exception("Test case requesting docstring specification is not "
                    "parameterized by any pool key: {}".format(", ".join(pks)))


class DocstringSpecification(object):
    """ Product type to model input parameter variation to docstring test. """

    def __init__(self, headline=None, detail=None, params=None, returns=None,
                 raises=None, pre_tags_space=False,
                 examples=None, trailing_space=False,
                 space_between_examples=True):
        """
        :param str headline: a short (ideally one-line) description
        :param str | Iterable[str] detail: longer, perhaps multi-line
            description for additional detail
        :param str | Iterable[str] params:
        :param str | Iterable[str] returns:
        :param str | Iterable[str] raises: blocks of text that define docstring
            exception tags
        :param bool pre_tags_space: whether to ensure a blank line before the
            tags section (provided the description is nonempty)
        :param str | Iterable[str] examples: block(s) of text that define
            code examples
        :param bool trailing_space: whether to ensure a blank line at the
            end of the docstring
        :param bool space_between_examples: whether to ensure a blank
            line between each example
        """

        # We want the return tag texts to be a collection
        if returns is None:
            returns = []
        elif isinstance(returns, str):
            returns = [returns]
        elif isinstance(returns, Iterable):
            if all(isinstance(r, str) for r in returns):
                returns = ["\n".join(returns)]
            elif all(isinstance(r, Iterable) and
                     not isinstance(r, str) for r in returns):
                returns = ["\n".join(rs) for rs in returns]
            else:
                returns = [rs if isinstance(rs, str) else "\n".join(rs)
                           for rs in returns]
                #raise Exception("Illegal returns argument: {}".format(returns))
        setattr(self, RET_KEY, returns)

        # Establish the docstring section settings.
        coll_atts = [SHORT_DESC_KEY, LONG_DESC_KEY, PAR_KEY, ERR_KEY, EXS_KEY]
        attr_vals = [headline, detail, params, raises, examples]
        for att, arg in zip(coll_atts, attr_vals):
            setattr(self, att, self._finalize_argument(arg))

        # Set the spacing parameters
        self.pre_tags_space = pre_tags_space
        self.trailing_space = trailing_space
        self.space_between_examples = space_between_examples

        # Sanity check on the value types
        non_lists = {a: getattr(self, a) for a in coll_atts
                     if not isinstance(getattr(self, a), list)}
        assert len(non_lists) == 0, "Non lists: {}".format(non_lists)

    @staticmethod
    def _finalize_argument(arg):
        """ Ensure that an argument of an expected type, and make into list. """
        if arg is None:
            return []
        if isinstance(arg, str):
            return arg.splitlines(False)
        if isinstance(arg, Iterable):
            return [obj if isinstance(obj, str) else "\n".join(obj)
                    for obj in arg]
        raise TypeError("Neither collection nor text: {} ({})".
                        format(arg, type(arg)))

    @property
    def all_tag_texts(self):
        """ Collection in which each element is the lines for one tag. """
        return self.params + self.returns + self.raises

    @property
    def exp_tag_count(self):
        """ Expected number of tags to be rendered (and later parsed) """
        return len(self.all_tag_texts)

    @property
    def exp_line_count(self):
        """ Expected number of lines in the rendition of this docstring """
        n = 0
        if self.headline:
            n += len(self.headline)
        print("POST HEADLINE: {}".format(n))
        if self.detail:
            n += len(self.detail)
        print("POST DETAIL: {}".format(n))
        if self.headline and self.detail:
            n += 1    # Intervening blank line
        print("POST FIRST BLANK: {}".format(n))
        print("ALL TAG TEXTS:\n{}".format(self.all_tag_texts))
        if self.has_tags:
            n += sum(tt.count("\n") + 1 for tt in self.all_tag_texts)
        print("POST HAS TAGS: {}".format(n))
        blank_lines_count = 0
        if self.has_tags and self.pre_tags_space and \
                (self.headline or self.detail):
            blank_lines_count += 1
        print("POST PRE TAGS SPACE BLANKS: {}".format(blank_lines_count))
        print("EXAMPLES:\n{}".format(self.examples))
        if self.examples:
            if self.headline or self.detail or self.has_tags:
                blank_lines_count += 1
            print("BLANKS EX 1: {}".format(blank_lines_count))
            n += sum(chunk.strip("\n").count("\n") +
                     (1 if self.space_between_examples else 0)
                     for chunk in self.examples)
            print("IN EXAMPLES: {}".format(n))
            blank_lines_count += (len(self.examples) - 1)
            print("BLANKS EX 2: {}".format(blank_lines_count))
        if self.trailing_space:
            blank_lines_count += 1
        print("POST TRAILING BLANKS: {}".format(blank_lines_count))
        n += blank_lines_count
        print("FINAL N: {}".format(n))
        return n

    @property
    def has_tags(self):
        """ Whether any tags are specified. """
        return self.exp_tag_count > 0

    def render(self):
        """
        Create the docstring encoded by this instance's composition.

        :return str: the docstring encoded by this instance's composition
        """
        headline = "\n".join(self.headline)
        detail = "\n".join(self.detail)
        desc_text = "{}\n\n{}".format(headline, detail) if headline and detail \
            else (headline or detail or "")
        if desc_text:
            desc_text += "\n"
        tags_text = "\n".join(self.all_tag_texts)
        examples_text = ("\n\n" if self.space_between_examples else "\n").\
            join(self.examples)
        if desc_text and tags_text:
            before_examples = "{}{}{}".format(
                desc_text, "\n" if self.pre_tags_space else "", tags_text)
        else:
            before_examples = desc_text or tags_text
        if before_examples and examples_text:
            ds = "{}\n\n{}".format(before_examples, examples_text)
        else:
            ds = before_examples or examples_text
        if not ds.endswith("\n"):
            ds += "\n"
        if self.trailing_space:
            print("ADDING TRAILING SPACE")
            ds += "\n"
        return ds.replace("\n\n\n", "\n\n")    # Clean up any double blanks.
