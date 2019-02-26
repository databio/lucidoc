#!/usr/bin/env python
# This script generates mkdocs friendly Markdown documentation from a python package.
# It is based on the the following blog post by Christian Medina
# https://medium.com/python-pandemonium/python-introspection-with-the-inspect-module-2c85d5aa5a48#.twcmlyack 

import argparse
import inspect
import itertools
import os
import pydoc
import sys
from .helpers import *
from .docstyle import get_styler, STYLERS
from .docparse import get_parser


module_header = "# Package {} Documentation\n"
class_header = "## Class {}"
function_header = "### {}"


__all__ = ["doc_class", "doc_callable", "doc_module"]


def _parse_args(cmdl):

    parser = argparse.ArgumentParser(
        description="Generate Markdown documentation for a module",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Required
    parser.add_argument(
        "module",
        help="Name/dotted path of module to document")
    parser.add_argument(
        "-P", "--parse", required=True,
        help="Name of parsing strategy for docstrings")

    # Optional
    parser.add_argument(
        "--append", action="store_true",
        help="Indicate that new docs should be appended to given file")
    parser.add_argument(
        "-O", "--output",
        help="Path to output file")
    parser.add_argument(
        "-S", "--style", choices=list(STYLERS.keys()),
        help="Name indicating which styler to use to render docstrings")

    return parser.parse_args(cmdl)


def doc_module(mod, docstr_parser, style_docstr):
    """
    Get large block of Markdown-formatted documentation of a module

    Parameters
    ----------
    mod : module
        Module to document in Markdown.
    docstr_parser : oradocle.DocstringParser
        How to parse a docstring.
    style_docstr : oradocle.DocstringStyler
        How to style/render a docstring.

    Returns
    -------
    str
        Large block of Markdown-formatted documentation of a module.

    """
    output = [module_header.format(mod.__name__)]
    if mod.__doc__:
        output.append(mod.__doc__)
    targets = _get_targets(mod)
    for n, t in targets:
        if inspect.isfunction(t) and not _unprotected(n):
            doc_chunks = doc_callable(t, docstr_parser, style_docstr)
        elif inspect.isclass(t) and _unprotected(n):
            doc_chunks = doc_class(t, docstr_parser, style_docstr)
        else:
            continue
        output.extend(doc_chunks)
    return "\n".join(str(x) for x in output)


def doc_class(cls, docstr_parser, style_docstr):
    """
    For single class definition, get text components for Markdown documentation.

    Parameters
    ----------
    cls : class
        Class to document with Markdown
    docstr_parser : oradocle.DocstringParser
        How to parse a docstring.
    style_docstr : callable
        How to style/render a docstring

    Returns
    -------
    list of str
        Text chunks constituting Markdown documentation for single class
        definition.

    """
    if not isinstance(cls, type):
        raise TypeError(_type_err_message(type, cls))

    def use_obj(name, _):
        return _unprotected(name)

    cls_doc = [class_header.format(cls.__name__),
               style_docstr(pydoc.inspect.getdoc(cls))]
    func_docs = _proc_objs(
        cls, lambda f: doc_callable(f, docstr_parser, style_docstr),
        pydoc.inspect.ismethod, use_obj)
    subcls_docs = _proc_objs(
        cls, lambda c: doc_class(c, docstr_parser, style_docstr),
        pydoc.inspect.isclass, use_obj)
    return cls_doc + func_docs + subcls_docs


def doc_callable(f, docstr_parser, style_docstr):
    """
    For single function get text components for Markdown documentation.

    Parameters
    ----------
    f : callable
        Function to document with Markdown
    docstr_parser : oradocle.DocstringParser
        How to parse a docstring.
    style_docstr : callable
        How to style/render a docstring

    Returns
    -------
    list of str
        Text chunks constituting Markdown documentation for single function.

    """
    if not is_callable_like(f):
        raise TypeError(_type_err_message(callable, f))

    n = f.__name__
    head = function_header.format(n.replace('_', '\\_'))
    signature = "def {}{}:\n".format(
        n, pydoc.inspect.formatargspec(*pydoc.inspect.getargspec(f)))

    res = [head]
    ds = pydoc.inspect.getdoc(f)
    if ds:
        desc_text, tags_text = docstr_parser.split_docstring(ds)
        res.extend([desc_text, "```python\n", signature, style_docstr(tags_text)])
    else:
        res.append(signature)
    res.extend(["```\n", "\n"])
    return res


def _get_targets(mod):
    """
    Determine given module's targets for documentation.

    Parameters
    ----------
    mod : module
        Module for which documentation targets should be found

    Returns
    -------
    Sequence of (str, object)
        (Ordered) collection of pairs--in which first component is object name
        and second is object itself--for documentation.

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

    Parameters
    ----------
    root : object
        The object from which to select contained objects.
    proc : function(object) -> Iterable of str
        How to process an individual subobject
    select : function(object) -> bool
        How to select subobjects from the root object, optional; this is passed
        as the predicate to inspect.getmembers
    pred : function(str, object) -> bool
        Additional filter for selected objects

    Returns
    -------
    list of str
        Collection of documentation chunks

    """
    pred = pred or (lambda _1, _2: True)
    return list(itertools.chain(*[
        proc(o) for n, o in inspect.getmembers(root, select) if pred(n, o)]))


def _type_err_message(exp_type, obs_value):
    """ Create message for TypeError when value doesn't match expectation. """
    return "Expected {} but got {} ({})".format(
            exp_type, obs_value, type(obs_value))


def _unprotected(name):
    """ Determine whether object name suggests its not protected. """
    return not name.startswith("_")


def main():
    """ Main workflow """
    opts = _parse_args(sys.argv[1:])
    modpath = opts.module
    try:
        sys.path.append(os.getcwd())
        # Attempt import
        mod = pydoc.safeimport(modpath)
        if mod is None:
            print("ERROR -- module not found: {}".format(modpath))
            raise SystemExit
    except pydoc.ErrorDuringImport:
        print("Error while trying to import module {}".format(modpath))
        raise
    else:
        parse = get_parser(opts.parse)
        style = get_styler(opts.style)
        doc = doc_module(mod, parse, style)
        if opts.output:
            outdir = os.path.dirname(opts.output)
            if outdir and not os.path.isdir(outdir):
                os.makedirs(outdir)
            msg, mode = ("Appending", 'a') if opts.append else ("Writing", 'w')
            print("{} docs: {}".format(msg, opts.output))
            with open(opts.output, mode) as f:
                f.write(doc)
            print("Done.")
        else:
            print(doc)


if __name__ == '__main__':
    main()
