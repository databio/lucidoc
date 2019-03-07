""" Package-level test data and fixtures """

import sys
if sys.version_info < (3, 3):
    from collections import Iterable
else:
    from collections.abc import Iterable
import pytest
from oradocle.docparse import RST_EXAMPLE_TAG

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


HEADLINE = "This is a short description."
DETAIL_LINES = ["This description provides more detail",
                "split over multiple lines.",
                "It may or may not have intervening or flanking blank line(s)."]

BOOL_PARAM = ":param bool flag: this quickly describes a flag"
FUNC_PARAM = ":param function(int, int) -> float: this maps two ints to a float"
ITER_PARAM = """
:param Iterable[Mapping[str, function(Iterable[float]) -> float]] func_maps: 
    this is a longer description, with too much content to be described on just 
    one line."""
UNION_PARAM = ":param str | Iterable[str] env: environment variables to try"

RETURN = ":return int: simple return code"
RETURN_MUTLI_LINE = """
:return str: this is a 
    multiline return comment"""
VALUE_ERROR = ":raise ValueError: if given an invalid particular arg val."
TYPE_ERROR = """
:raise TypeError: if one of the given arguments 
    is of an unacceptable type
"""

DESCRIPTION_ELEMENTS = [HEADLINE, DETAIL_LINES]
PARAM_LINES = [BOOL_PARAM, FUNC_PARAM, ITER_PARAM, UNION_PARAM]



@pytest.fixture(scope="function", params=[])
def ds_spec(request):
    return request.param


CODE_EXAMPLE_TEXT = """
{ex_tag}

.. code-block:: python

    from a import b
    c = 3

{ex_tag}

.. code-block:: python

    text = "this is the second example"
    text += " and should parse separately from the first"
""".format(ex_tag=RST_EXAMPLE_TAG)


class DocstringTestInput(object):
    """ Product type to model input parameter variation to docstring test. """

    def __init__(self, headline=None, detail=None, params=None, returns=None,
                 raises=None, pre_tags_space=False, pre_examples_space=False,
                 examples=None, trailing_space=False):
        coll_atts = ["headline", "detail", "params", "returns", "raises", "examples"]
        attr_vals = [headline, detail, params, returns, raises, examples]
        for att, arg in zip(coll_atts, attr_vals):
            setattr(self, att, self._finalize_argument(arg))
        self.pre_tags_space = pre_tags_space
        self.pre_examples_space = pre_examples_space
        self.examples = examples
        self.trailing_space = trailing_space
        assert all(isinstance(getattr(self, a), list) for a in coll_atts)

    @staticmethod
    def _finalize_argument(arg):
        """ Ensure that an argument of an expected type, and make into list. """
        if arg is None:
            return []
        if isinstance(arg, str):
            return arg.splitlines(keepends=False)
        if isinstance(arg, Iterable):
            return [obj if isinstance(obj, str) else "\n".join(obj)
                    for obj in arg]
        raise TypeError("Neither collection nor text: {} ({})".
                        format(arg, type(arg)))

    @property
    def all_tag_line_chunks(self):
        return self.params + self.returns + self.raises

    @property
    def exp_tag_count(self):
        return len(self.all_tag_line_chunks)

    @property
    def exp_line_count(self):
        n = 0
        if self.headline:
            n += len(self.headline)
        if self.detail:
            n += len(self.detail)
        if self.headline and self.detail:
            n += 1    # Intervening blank line
        if self.has_tags:
            n += sum(len(c) for c in self.all_tag_line_chunks)
        blank_lines_count = 0
        if self.trailing_space:
            blank_lines_count += 1
        if self.examples and self.pre_examples_space and self.has_tags:
            blank_lines_count += 1
        if self.has_tags and self.pre_tags_space and (self.header or self.detail):
            blank_lines_count += 1
        if self.header and self.detail:
            blank_lines_count += 1
        n += blank_lines_count
        return n

    @property
    def has_tags(self):
        return len(self.all_tag_line_chunks) > 0

    def render(self):
        """
        Create the docstring encoded by this instance's composition.

        :return str: the docstring encoded by this instance's composition
        """
        if self.headline and self.detail:
            desc_text = "{}\n{}".format(self.headline, "\n".join(self.detail))
        else:
            desc_text = self.headline or self.detail or ""
        tags_text = "\n".join(self.all_tag_line_chunks)
        examples_text = "\n".join(self.examples)
        if desc_text and tags_text:
            before_examples = "{}{}{}".format(
                desc_text, "\n" if self.pre_tags_space else "", tags_text)
        else:
            before_examples = desc_text or tags_text
        if before_examples and examples_text:
            ds = "{}{}{}".format(
                before_examples, "\n" if self.pre_examples_space else "",
                examples_text)
        else:
            ds = before_examples or examples_text
        return ds


# DEBUG
print("CODE TEXT: {}".format(CODE_EXAMPLE_TEXT))
CODE_LINES = CODE_EXAMPLE_TEXT.splitlines(keepends=False)
print("{} code lines: {}".format(len(CODE_LINES), CODE_LINES))

