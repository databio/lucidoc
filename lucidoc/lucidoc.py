#!/usr/bin/env python
"""
Generate mkdocs-friendly API documentation for a Python package.

This program parses docstrings from objects defined in a Python package and
uses the information from those docstrings to generate mkdocs-friendly
documentation in Markdown format. Essentially, therefore, it generates
API documentation for the package.

"""

import argparse
import inspect
import itertools
import os
import pydoc
import sys
from .helpers import *
from .docparse import get_parser, RST_KEY
from .doctags import MdTagRenderer
from .exceptions import lucidocError
from ._version import __version__

module_header = "# Package {} Documentation\n"
class_header = "## Class {}"
function_header = "### {}"


__all__ = ["doc_class", "doc_callable", "doc_module", "run_lucidoc"]


class _VersionInHelpParser(argparse.ArgumentParser):
    def format_help(self):
        """ Add version information to help text. """
        return "version: {}\n".format(__version__) + \
               super(_VersionInHelpParser, self).format_help()


def _parse_args(cmdl):

    parser = _VersionInHelpParser(
        description="Generate Markdown documentation for a module",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-V", "--version",
        action="version",
        version="%(prog)s {v}".format(v=__version__))

    # Required
    parser.add_argument(
        "pkgpath",
        help="Name/dotted path to package to document, i.e. what you'd type as "
             "the target for an import statement")
    parser.add_argument(
        "-P", "--parse", choices=[RST_KEY], required=True,
        help="Name of parsing strategy for docstrings")

    # Optional
    parser.add_argument(
        "--skip-module-docstring", action="store_true",
        help="Indicate that module docstring should be omitted")
    parser.add_argument(
        "--inherited", action="store_true",
        help="Include inherited members")
    parser.add_argument(
        "-O", "--output",
        help="Path to output file")

    return parser.parse_args(cmdl)


def doc_module(mod, docstr_parser, render_tag,
               no_mod_docstr=False, include_inherited=False):
    """
    Get large block of Markdown-formatted documentation of a module

    :param module mod: module to document in Markdown.
    :param lucidoc.DocstringParser docstr_parser: how to parse a docstring.
    :param callable(lucidoc.DocTag) -> str render_tag: how to render a tag
        parsed from a docstring; the argument should be total. In other words,
        each potential type of tag that may be passed to it as an argument
        should be accounted for in the implementation.
    :param bool no_mod_docstr: skip module-level docstring
    :param bool include_inherited: include inherited members
    :return str: Large block of Markdown-formatted documentation of a module.
    """
    output = [module_header.format(mod.__name__)]
    if mod.__doc__ and not no_mod_docstr:
        output.append(mod.__doc__)
    targets = _get_targets(mod)
    print(os.linesep.join(["All doc targets:"] + [n for n, _ in targets]))
    classes, functions = [], []
    for n, t in targets:
        if inspect.isfunction(t) and _unprotected(n):
            functions.append(t)
        elif inspect.isclass(t) and _unprotected(n):
            classes.append(t)
        else:
            print("Skipping: {}".format(n))
            continue
    for doc_obj in classes:
        output.extend(doc_class(doc_obj, docstr_parser, render_tag, include_inherited))
    for doc_obj in functions:
        output.extend(doc_callable(doc_obj, docstr_parser, render_tag))
    return "\n".join(str(x) for x in output)


def doc_class(cls, docstr_parser, render_tag, include_inherited):
    """
    For single class definition, get text components for Markdown documentation.

    :param class cls: class to document with Markdown
    :param lucidoc.DocstringParser docstr_parser: How to parse a docstring.
    :param callable(lucidoc.DocTag) -> str render_tag: how to render an
        individual tag from a docstring. The implementation in the object
        passed as an argument should handle each type of DocTag that
        may be passed as an argument when this object is called.
    :param bool include_inherited: include inherited members
    :return list[str]: text chunks constituting Markdown documentation for
        single class definition.
    """

    # TODO: handle parse of __init__ as alternative/supplement to class docstring.

    if not isinstance(cls, type):
        raise TypeError(_type_err_message(type, cls))

    # Arbiter of whether a class member should be documented.
    def use_obj(name, _):
        return _unprotected(name)

    print("Processing class: {}".format(cls.__name__))

    cls_doc = [class_header.format(cls.__name__)]
    class_docstr = pydoc.inspect.getdoc(cls)
    if class_docstr:
        parsed_clsdoc = docstr_parser(class_docstr)
        parsed_clsdoc.desc and cls_doc.append(parsed_clsdoc.desc + "\n")
        param_tag_lines = [render_tag(t) for t in parsed_clsdoc.params]
        err_tag_lines = [render_tag(t) for t in parsed_clsdoc.raises]
        block_lines = []
        if param_tag_lines:
            block_lines.append("**Parameters:**\n")
            block_lines.extend(param_tag_lines)
            block_lines.append("\n")
        if parsed_clsdoc.returns:
            raise lucidocError("Class docstring has a return value: {}".
                              format(parsed_clsdoc.returns))
        if err_tag_lines:
            block_lines.append("**Raises:**\n")
            block_lines.extend(err_tag_lines)
            block_lines.append("\n")
        if parsed_clsdoc.examples:
            if not isinstance(parsed_clsdoc.examples, list):
                raise TypeError("Example lines are {}, not list".format(type(parsed_clsdoc.examples)))
            block_lines.append("**Example(s):**\n")
            block_lines.extend(parsed_clsdoc.examples)
            block_lines.append("\n")
        block = "\n".join(block_lines)
        cls_doc.append(block)

    # TODO: account for inherited properties, not just methods
    eligible = lambda o: (pydoc.inspect.ismethod(o) or isinstance(o, property))

    def inherited(f):
        try:
            parents = cls.__bases__
        except AttributeError:
            return False
        for p in parents:
            try:
                if getattr(p, f.__name__) == f:
                    return True
            except AttributeError:
                continue
        return False

    if include_inherited:
        def use_as_fun(o):
            return eligible(o)
    else:
        def use_as_fun(o):
            return eligible(o) and (isinstance(o, property) or not inherited(o))

    func_docs = _proc_objs(
        cls,
        lambda n, f: doc_callable(f, docstr_parser, render_tag, name=n),
        use_as_fun, use_obj)
    subcls_docs = _proc_objs(
        cls, lambda c: doc_class(c, docstr_parser, render_tag, include_inherited),
        pydoc.inspect.isclass, use_obj)
    return cls_doc + func_docs + subcls_docs


def _get_class_docstring(cls):
    if not inspect.isclass(cls):
        raise TypeError("Attempted to get class docstring for a non-class "
                        "object: {}".format(cls))
    init_func = [o for n, o in inspect.getmembers(cls) if
                 n == "__init__" and inspect.ismethod(o)]
    header_cls_doc = pydoc.inspect.getdoc(cls)
    init_cls_doc = pydoc.inspect.getdoc(init_func)
    if header_cls_doc and init_cls_doc:
        raise ValueError("Both header docstring and constructor docstring are "
                         "present for {}".format(cls.__name__))


def doc_callable(f, docstr_parser, render_tag, name=None):
    """
    For single function get text components for Markdown documentation.

    :param callable | property f: function or property to document
    :param lucidoc.DocstringParser docstr_parser: How to parse a docstring.
    :param callable(lucidoc.DocTag) -> str render_tag: how to render an
        individual tag from a docstring. The implementation in the object
        passed as an argument should handle each type of DocTag that
        may be passed as an argument when this object is called.
    :param str name: name of object being documented; pass directly for prop.
    :return list[str]: text chunks constituting Markdown documentation for
        single function.

    """
    if not is_callable_like(f):
        raise TypeError(_type_err_message(callable, f))

    if name:
        n = name
    else:
        try:
            n = f.__name__
        except AttributeError:
            raise lucidocError("No name for object of {}; explicitly pass name "
                              "if documenting a property".format(type(f)))

    print("Processing function: {}".format(n))

    head = function_header.format(n.replace('_', '\\_'))

    try:
        pars = pydoc.inspect.formatargspec(*pydoc.inspect.getargspec(f))
    except TypeError:
        pars = None
    signature = "```python\ndef {}{}:\n```\n".format(n, pars or "")

    res = [head]
    ds = pydoc.inspect.getdoc(f)
    if ds:
        parsed = docstr_parser(ds)
        param_tag_lines = [render_tag(t) for t in parsed.params]
        err_tag_lines = [render_tag(t) for t in parsed.raises]
        block_lines = []
        if param_tag_lines:
            block_lines.append("**Parameters:**\n")
            block_lines.extend(param_tag_lines)
            block_lines.append("\n")
        if parsed.returns:
            block_lines.append("**Returns:**\n")
            block_lines.append(render_tag(parsed.returns))
            block_lines.append("\n")
        if err_tag_lines:
            block_lines.append("**Raises:**\n")
            block_lines.extend(err_tag_lines)
            block_lines.append("\n")
        block = "\n".join(block_lines)
        res.extend([docstr_parser.description(ds), signature, block])
    else:
        res.append(signature)
    res.append("\n")
    return res


def _get_targets(mod):
    """
    Determine given module's targets for documentation.

    :param module mod: module for which documentation targets should be found
    :return Sequence[(str, object)]: (Ordered) collection of pairs for
        documentation, in which first component is object name and second is
        object itself.
    """
    try:
        exports = mod.__all__
    except AttributeError:
        return inspect.getmembers(mod)
    objs, missing = [], []
    for name in exports:
        try:
            objs.append((name, getattr(mod, name)))
        except AttributeError:
            missing.append(name)
    if missing:
        raise Exception("Module is missing declared export(s): {}".
                        format(", ".join(missing)))
    return objs


def _proc_objs(root, proc, select=None, pred=None):
    """
    Process selected objects, within a "root" object, that satisfy a predicate.

    :param object root: the object from which to select contained objects
    :param function(object) -> Iterable[str] proc: how to process an individual
        subobject
    :param function(object) -> bool select: how to select subobjects from the
        root object, optional; this is passed as the predicate to
        inspect.getmembers
    :param callable(str, object) -> bool pred: Additional filter for selected
        objects
    :return list[str]: collection of documentation chunks
    """
    pred = pred or (lambda _1, _2: True)
    nargs = len(inspect.getargspec(proc).args)
    if nargs == 1:
        do = lambda _, o: proc(o)
    elif nargs == 2:
        do = lambda n, o: proc(n, o)
    else:
        raise ValueError("Processing function should take exactly 1 or 2 "
                         "arguments, not {}".format(nargs))
    return list(itertools.chain(*[
        do(n, o) for n, o in inspect.getmembers(root, select) if pred(n, o)]))


def _type_err_message(exp_type, obs_value):
    """ Create message for TypeError when value doesn't match expectation. """
    return "Expected {} but got {} ({})".format(
            exp_type, obs_value, type(obs_value))


def _unprotected(name):
    """ Determine whether object name suggests its not protected. """
    return not name.startswith("_")


"""
def get_module_paths(root, subs=None):
    """"""
    Get dotted paths to modules to document.

    :param str root: filepath to from which to begin module search
    :param Iterable[str] subs: subpaths used so far
    :return Iterable[stri]: collection of dotted paths to modules to document
    """"""

    if not os.path.isdir(root):
        raise lucidocError("Package root path isn't a folder: {}".format(root))

    _, pkgname = os.path.split(root)

    mod_file_paths = []

    def make_mod_path(p, priors):
        return ".".join(priors + [os.path.splitext(os.path.split(p)[1])[0]])

    for r, ds, fs in os.walk(root):
        mod_file_paths.extend(map(lambda f: os.path.join(r, f), fs))
        for d in ds:
            if d.startswith("_"):
                continue
            mod_file_paths.extend(get_module_paths(os.path.join(r, d)))

    def keep(p):
        _, fn = os.path.split(p)
        return fn.endswith(".py") and not fn.startswith("_")

    return list(map(make_mod_path, filter(keep, mod_file_paths)))
"""


def run_lucidoc(pkg, parse_style, outfile,
               no_mod_docstr=False, include_inherited=False):
    try:
        sys.path.append(os.getcwd())
        # Attempt import
        mod = pydoc.safeimport(pkg)
        if mod is None:
            raise lucidocError("ERROR -- Target object for documentation not "
                              "found: {}".format(pkg))
    except pydoc.ErrorDuringImport:
        print("Error while trying to import module {}".format(pkg))
        raise
    else:
        show_tag = MdTagRenderer()
        parse = get_parser(parse_style)
        doc = doc_module(mod, parse, show_tag, no_mod_docstr, include_inherited)
        if outfile:
            outdir = os.path.dirname(outfile)
            if outdir and not os.path.isdir(outdir):
                os.makedirs(outdir)
            print("Writing docs: {}".format(outfile))
            with open(outfile, 'w') as f:
                f.write(doc)
            print("Done.")
        else:
            print(doc)


def main():
    """ Main workflow """
    opts = _parse_args(sys.argv[1:])
    run_lucidoc(opts.pkgpath, opts.parse, opts.output,
               opts.skip_module_docstring)
    

if __name__ == '__main__':
    main()
