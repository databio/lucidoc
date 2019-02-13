#!/usr/bin/env python
# This script generates mkdocs friendly Markdown documentation from a python package.
# It is based on the the following blog post by Christian Medina
# https://medium.com/python-pandemonium/python-introspection-with-the-inspect-module-2c85d5aa5a48#.twcmlyack 

import argparse
import inspect
import os
import pydoc
import sys

module_header = "# Package {} Documentation\n"
class_header = "## Class {}"
function_header = "### {}"


__all__ = ["doc_class", "doc_callable", "doc_module"]


def _parse_args(cmdl):
    parser = argparse.ArgumentParser(
        description="Generate Markdown documentation for a module",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("module", help="Name/dotted path of module to document")
    return parser.parse_args(cmdl)


def doc_module(mod):
    """
    Get large block of Markdown-formatted documentation of a module

    Parameters
    ----------
    mod : module
        Module to document in Markdown.

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
            doc_chunks = doc_callable(t)
        elif inspect.isclass(t) and _unprotected(n):
            doc_chunks = doc_class(t)
        else:
            continue
        output.extend(doc_chunks)
    return "\n".join(str(x) for x in output)


def doc_class(cls):
    """
    For single class definition, get text components for Markdown documentation.

    Parameters
    ----------
    cls : class
        Class to document with Markdown

    Returns
    -------
    list of str
        Text chunks constituting Markdown documentation for single class
        definition.

    """
    if not isinstance(cls, type):
        raise TypeError(_type_err_message(type, cls))
    cls_doc = [class_header.format(cls.__name__), pydoc.inspect.getdoc(cls)]
    func_docs = [doc_callable(f) for n, f in 
                 pydoc.inspect.getmembers(cls, pydoc.inspect.ismethod)
                 if (_unprotected(n) or n == "__init__")]
    subcls_docs = [doc_class(c) for n, c in
                   inspect.getmembers(cls, inspect.isclass)
                   if _unprotected(n)]
    return cls_doc + func_docs + subcls_docs


def doc_callable(f):
    """
    For single function get text components for Markdown documentation.

    Parameters
    ----------
    f : callable
        Function to document with Markdown

    Returns
    -------
    list of str
        Text chunks constituting Markdown documentation for single function.

    """
    if not hasattr(f, "__call__"):
        raise TypeError(_type_err_message(callable, f))

    n = f.__name__
    head = function_header.format(n.replace('_', '\\_'))
    sign = 'def %s%s\n' % (n, pydoc.inspect.formatargspec(*pydoc.inspect.getargspec(f)))

    res = [head, '```py\n', sign, '```\n']

    # Add for docstring if present.
    ds = pydoc.inspect.getdoc(f)
    ds and res.extend(['\n', ds])

    res.append('\n')
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
            print("Module not found")
        # Module imported correctly, let's create the docs
        return doc_module(mod)
    except pydoc.ErrorDuringImport as e:
        print("Error while trying to import module {} -- {}".format(modpath, e))


if __name__ == '__main__':
    print(main())
