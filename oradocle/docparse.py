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
from .doctags import *
from .exceptions import OradocError


__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["DocstringParser", "ParsedDocstringResult",
           "RstDocstringParser", "get_parser"]


RST_EXAMPLE_TAG = ":Example:"


ParsedDocstringResult = namedtuple(
    "ParsedDocstringResult",
    ["doc", "desc", "params", "returns", "raises", "example"])


class DocstringParser(object):
    """ Entity responsible for parsing docstrings """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self, ds):
        """
        Fully parse the given docstring.

        :param str ds: The docstring to parse.
        :return oradocle.ParsedDocstringResult: The complete result of parsing
            the given docstring.
        """
        pass

    @abc.abstractmethod
    def description(self, ds):
        """
        Parse the description portion of a docstring.

        :param str ds: docstring from which to parse description
        :return str: description portion of docstring
        """
        pass

    @abc.abstractmethod
    def params(self, ds):
        """
        Parse parameter tags from docstring.

        :param str ds: docstring from which to parse parameter tags
        :return Iterable[oradocle.ParTag]: (possibly empty) collection of
            parameter tags parsed from the given docstring
        """
        pass

    @abc.abstractmethod
    def returns(self, ds):
        """
        Parse parameter tags from docstring.

        :param str ds: docstring from which to parse result tag
        :return oradocle.RetTag | NoneType: (possibly empty) collection of
            parameter tags parsed from the given docstring
        """
        pass

    @abc.abstractmethod
    def raises(self, ds):
        """
        Parse parameter tags from docstring.

        :param str ds: docstring from which to parse result tag
        :return Iterable[oradocle.ErrTag]: (possibly empty) collection of
            parameter tags parsed from the given docstring
        """
        pass


class RstDocstringParser(DocstringParser):
    """ Parser for ReStructured text docstrings. """

    def __init__(self):
        """ Set the most recently seen docstring parse result to null. """
        super(RstDocstringParser, self).__init__()
        self._last_seen = None

    def __call__(self, ds):
        return self._last_seen if self._cached(ds) else self._parse(ds)

    def description(self, ds):
        return self._fetchparse(ds, "desc")

    def params(self, ds):
        return self._fetchparse(ds, "params")

    def returns(self, ds):
        return self._fetchparse(ds, "returns")

    def raises(self, ds):
        return self._fetchparse(ds, "raises")

    def example(self, ds):
        """
        Get the code example text from a docstring.

        :param str ds: docstring from which to parse example
        :return str: code example text from docstring
        """
        return self._fetchparse(ds, "example")

    def _fetchparse(self, ds, name):
        """ Return cached result if available, else parse then cache. """
        return getattr(self._last_seen, name) if self._cached(ds) else \
            self._parse(ds, name)

    @staticmethod
    def _is_blank(l):
        return l.strip() == ""

    def _cached(self, ds):
        return self._last_seen is not None and self._last_seen.doc == ds

    def _get_tag(self, chunk):
        """ Create the tag associated with a chunk of docstring lines. """
        try:
            decl_line = chunk[0]
        except IndexError:
            raise OradocError("Empty tag chunk")
        tag_type, args = self._parse_tag_start(decl_line)
        if len(chunk) > 1:
            args[-1] = args[-1] + " ".join(l.lstrip() for l in chunk[1:])
        tag = tag_type(*args)
        return tag

    @staticmethod
    def _is_tag_start(l):
        """ Determine whether line seems to start a tag declaration. """
        return l.startswith(":")

    def _parse(self, ds, name=None):
        """ Parse the description, examples, and tags from a docstring. """
        lines = ds.split(os.linesep)

        def seek_past_head(ls):
            h = []
            for i, l in enumerate(ls):
                if self._is_blank(l) or self._is_tag_start(l):
                    return h, i
                h.append(l)
            else:
                return h, len(ls)

        head, non_head_index = seek_past_head(lines)
        #if not head:
        #    raise OradocError("Empty docstring")
        head = " ".join(l.strip() for l in head)

        ls1, ls2 = tee(lines[non_head_index:])
        detail_lines = list(filterfalse(
            self._is_blank, takewhile(lambda l: not self._is_tag_start(l), ls1)))
        desc = head
        if detail_lines:
            desc += ("\n\n" if desc else "" + "\n".join(detail_lines))
        post_desc = list(dropwhile(lambda l: not self._is_tag_start(l), ls2))

        raw_tag_blocks = []
        if post_desc and self._is_tag_start(post_desc[0]):
            curr_block = []
            for i, l in enumerate(post_desc):
                if self._is_blank(l):
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
            curr_block and raw_tag_blocks.append(curr_block)
        else:
            first_non_tag_index = 0

        ex_lines = self._parse_example_lines(
            [] if first_non_tag_index is None
            else post_desc[first_non_tag_index:])

        tags = [self._get_tag(chunk) for chunk in raw_tag_blocks]

        par, ret, err = [], [], []
        for t in tags:
            if isinstance(t, ParTag):
                par.append(t)
            elif isinstance(t, RetTag):
                ret.append(t)
            elif isinstance(t, ErrTag):
                err.append(t)
            else:
                raise TypeError("Unrecognized doc tag type: {}".format(type(t)))

        if len(ret) > 1:
            raise ValueError("Multiple ({}) returns tags: {}".
                             format(len(ret), ret))
        ret = ret[0] if ret else None

        self._last_seen = ParsedDocstringResult(ds, desc, par, ret, err, ex_lines)
        return (name and getattr(self._last_seen, name)) or self._last_seen

    @staticmethod
    def _parse_tag_start(line):
        """ Parse first of a chunk of lines associated with a docstring tag. """
        if line.startswith(":param"):
            tt = ParTag
        elif line.startswith(":returns") or line.startswith(":return"):
            tt = RetTag
        elif line.startswith(":raise") or line.startswith(":raises"):
            tt = ErrTag
        else:
            raise OradocError("Invalid tag declaration start: " + line)
        colon_chunks = line.split(":")
        left_parts, desc = colon_chunks[1:-1], colon_chunks[-1]
        if issubclass(tt, ParTag):
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

        ex_section_start = RST_EXAMPLE_TAG
        tag_code_block = ".. code-block::"
        default_code_name = "console"
        bookend = "```"

        def err_msg():
            return "Could not parse example section lines: {}".format(ls)

        if head.startswith(bookend):
            return ls
        elif head.startswith(ex_section_start):
            code_type_lines = list(takewhile(
                lambda l: not self._is_blank(l), dropwhile(self._is_blank, ls[1:])))
            if len(code_type_lines) == 1:
                code_type = code_type_lines[0].lstrip(tag_code_block).strip()
            elif len(code_type_lines) == 0:
                code_type = default_code_name
            else:
                raise OradocError(err_msg())
            in_section_head = lambda l: self._is_blank(l) or \
                l.startswith(tag_code_block) or l.startswith(RST_EXAMPLE_TAG)
            content_lines = list(dropwhile(in_section_head, ls))
            block_start = bookend + (code_type or default_code_name)
            return [block_start] + [l.lstrip() for l in content_lines] + [bookend]


RST_KEY = "rst"
PARSERS = {RST_KEY: RstDocstringParser()}


class UnknownParserError(OradocError):
    """ Exception for request of unsupported parsing strategy. """

    def __init__(self, name):
        msg = "{}; choose one: {}".format(name, ", ".join(PARSERS.keys()))
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
        return PARSERS[name]
    except KeyError:
        raise UnknownParserError(name)
