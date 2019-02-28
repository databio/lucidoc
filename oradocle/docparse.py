""" Docstring parsing """

import abc
from collections import namedtuple
from itertools import dropwhile, takewhile, tee
import os
import sys
if sys.version_info < (3, 0):
    from itertools import ifilterfalse as filterfalse
else:
    from itertools import filterfalse
from .exceptions import OradocleError
from .helpers import cleanly_join_lines

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["DocstringParser", "RstDocstringParser", "get_parser"]


ParsedDocstringResult = namedtuple(
    "ParsedDocstringResult",
    ["doc", "desc", "params", "returns", "raises", "example"])
ParamDoc = namedtuple("ParamDoc", ["name", "typename", "description"])
ReturnsDoc = namedtuple("ReturnsDoc", ["typename", "description"])
RaisesDoc = namedtuple("RaisesDoc", ["typename", "description"])


class DocstringParser(object):
    """ Entity responsible for parsing docstrings """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def description(self, ds):
        pass

    @abc.abstractmethod
    def detail(self, ds):
        pass

    @abc.abstractmethod
    def params(self, ds):
        pass

    @abc.abstractmethod
    def returns(self, ds):
        pass

    @abc.abstractmethod
    def raises(self, ds):
        pass


class RstDocstringParser(DocstringParser):
    """ Parser for ReStructured text docstrings. """

    def __init__(self):
        super(RstDocstringParser, self).__init__()
        self._last_seen = None

    def header(self, ds):
        try:
            return self.description(ds)[0]
        except IndexError:
            raise Exception("Empty docstring")

    @staticmethod
    def _blank(l):
        return l.strip() == ""

    def detail(self, ds):
        full_desc = self.description(ds)
        return list(takewhile(
            lambda l: not self._blank(l),
            dropwhile(self._blank, full_desc.split(os.linesep)[1:])))

    def description(self, ds):
        name = "desc"
        return getattr(self._last_seen, name) if self._cached(ds) else \
            self._parse(ds, name)

    def params(self, ds):
        name = "params"
        return getattr(self._last_seen, name) if self._cached(ds) else \
            self._parse(ds, name)

    def returns(self, ds):
        name = "returns"
        return getattr(self._last_seen, name) if self._cached(ds) else \
            self._parse(ds, name)

    def raises(self, ds):
        name = "raises"
        return getattr(self._last_seen, name) if self._cached(ds) else \
            self._parse(ds, name)

    def example(self, ds):
        name = "example"
        return getattr(self._last_seen, name) if self._cached(ds) else \
            self._parse(ds, name)

    def _cached(self, ds):
        # DEBUG
        if self._last_seen is None:
            return False
        print("Checking CACHE")
        print("DOCSTRING: {}".format(ds))
        print("CURR: {}".format(self._last_seen))
        print("equal?: {}".format(self._last_seen.doc == ds))
        return self._last_seen is not None and self._last_seen.doc == ds

    @staticmethod
    def _is_tag_start(l):
        """ Determine whether line seems to start a tag declaration. """
        return l.startswith(":")

    def _parse(self, ds, name=None):
        # DEBUG
        print("PARSING")
        lines = ds.split(os.linesep)

        try:
            head = lines[0]
        except IndexError:
            raise Exception("Empty docstring")

        ls1, ls2 = tee(lines[1:])
        detail_lines = list(filterfalse(
            self._blank, takewhile(lambda l: not self._is_tag_start(l), ls1)))
        desc = cleanly_join_lines([head] + detail_lines)
        post_desc = list(filterfalse(
            self._blank, dropwhile(lambda l: not self._is_tag_start(l), ls2)))

        raw_tag_blocks = []
        if post_desc and self._is_tag_start(post_desc[0]):
            curr_block = []
            for i, l in enumerate(post_desc):
                if self._blank(l):
                    first_non_tag_index = i + 1
                    break
                l = l.strip()
                if self._is_tag_start(l):
                    if curr_block:
                        raw_tag_blocks.append(curr_block)
                    curr_block = [l]
                else:
                    curr_block.append(l)
            else:
                first_non_tag_index = None
        else:
            first_non_tag_index = 0

        ex_lines = self._parse_example_lines(
            [] if first_non_tag_index is None
            else post_desc[first_non_tag_index:])

        tags = [self._get_tag(chunk) for chunk in raw_tag_blocks]
        par, ret, err = [], [], []
        for t in tags:
            if isinstance(t, ParamDoc):
                par.append(t)
            elif isinstance(t, ReturnsDoc):
                ret.append(t)
            elif isinstance(t, RaisesDoc):
                err.append(t)
            else:
                raise TypeError("Unrecognized doc tag type: {}".format(type(t)))
        if len(ret) > 1:
            raise ValueError("Multiple ({}) returns tags: {}".
                             format(len(ret), ret))
        ret = ret[0] if ret else None

        self._last_seen = ParsedDocstringResult(ds, desc, par, ret, err, ex_lines)
        res = (name and getattr(self._last_seen, name)) or self._last_seen
        # DEBUG
        print("REQUESTED: {}".format(name))
        print("type(res): {}".format(type(res)))
        return res

    def _get_tag(self, chunk):
        """ Create the tag associated with a chunk of docstring lines. """
        try:
            decl_line = chunk[0]
        except IndexError:
            raise Exception("Empty tag chunk")
        tag_type, args = self._parse_tag_start(decl_line)
        if len(chunk) > 1:
            desc = args[-1] if isinstance(args[-1], list) else [args[-1]]
            args[-1] = desc + desc + [l.lstrip() for l in chunk[1:]]
        tag = tag_type(*args)
        return tag

    def _parse_tag_start(self, line):
        """ Parse first of a chunk of lines associated with a docstring tag. """
        if line.startswith(":param"):
            tt = ParamDoc
        elif line.startswith(":returns") or line.startswith(":return"):
            tt = ReturnsDoc
        elif line.startswith(":raise") or line.startswith(":raises"):
            tt = RaisesDoc
        else:
            raise Exception("Invalid tag declaration start: " + line)
        colon_chunks = line.split(":")
        left_parts, desc = colon_chunks[1:-1], colon_chunks[-1]
        if issubclass(tt, ParamDoc):
            mid_parts = left_parts[0].split(" ")
            name = mid_parts[-1]
            typename = " ".join(mid_parts[1:-1])
            args = [name, typename, desc]
        else:
            typename = " ".join(left_parts[0].split(" ")[1:])
            args = [typename, desc]
        return tt, args

    def _parse_example_lines(self, ls):
        """ Parse the example portion of a docstring. """
        if not ls:
            return None
        try:
            head = ls[0]
        except IndexError:
            return None

        tag_code_block = ".. code-block::"
        default_code_name = "console"
        bookend = "```"

        def err_msg():
            return "Could not parse example section lines: {}".format(ls)

        if head.startswith(bookend):
            return ls
        elif head.startswith(":Example:"):
            code_type_lines = list(takewhile(
                lambda l: not self._blank(l), dropwhile(self._blank, ls[1:])))
            if len(code_type_lines) == 1:
                code_type = code_type_lines[0].lstrip(tag_code_block).strip()
            elif len(code_type_lines) == 0:
                code_type = default_code_name
            else:
                raise Exception(err_msg())
            content_lines = list(dropwhile(
                lambda l: self._blank(l) or l.startswith(tag_code_block), ls))
            block_start = bookend + (code_type or default_code_name)
            return [block_start] + [l.lstrip() for l in content_lines] + [bookend]


RST_KEY = "rst"
STYLERS = {RST_KEY: RstDocstringParser()}


class UnknownParserError(OradocleError):
    """ Exception for request of unsupported parsing strategy. """

    def __init__(self, name):
        msg = "{}; choose one: {}".format(name, ", ".join(STYLERS.keys()))
        super(UnknownParserError, self).__init__(msg)


def get_parser(name):
    """
    Get a docstring parsing strategy.

    :param str name: Key for a parsing strategy.
    :return oradocle.DocstringParser: The parser to which the given name is
        mapped.
    :raise oradocle.UnknownParserError: If given a nonempty name that's not
        mapped to a parser.
    """
    try:
        return STYLERS[name]
    except KeyError:
        raise UnknownParserError(name)
