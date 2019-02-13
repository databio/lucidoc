#!/usr/bin/env python
# This script generates mkdocs friendly Markdown documentation from a python package.
# It is based on the the following blog post by Christian Medina
# https://medium.com/python-pandemonium/python-introspection-with-the-inspect-module-2c85d5aa5a48#.twcmlyack 

import inspect
import os
import pydoc
import sys

module_header = "# Package {} Documentation\n"
class_header = "## Class {}"
function_header = "### {}"


__all__ = ["doc_class", "doc_callable", "doc_module", "get_mod_doc"]


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


def _is_docable_class(obj):
    return inspect.isclass(obj) and not obj.__name__.startswith("_")


def _unprotected(name):
    return not name.startswith("_")


def _get_targets(mod):
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


def get_mod_doc(modname):
    """
    Generate Markdown documentation for classes and functions in a module.

    Parameters
    ----------
    modname : str
        The module in which to search for (unprotected) classes and functions
        for which Markdown documentation should be generated.

    Returns
    -------
    str
        Large block of Markdown-formatted documentation of a module.

    """
    try:
        sys.path.append(os.getcwd())
        # Attempt import
        mod = pydoc.safeimport(modname)
        if mod is None:
            print("Module not found")
        # Module imported correctly, let's create the docs
        return doc_module(mod)
    except pydoc.ErrorDuringImport as e:
        print("Error while trying to import module {} -- {}".format(modname, e))


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
    # DEBUG
    print("DOCING CLASS: {}".format(cls.__name__))
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


def _type_err_message(exp_type, obs_value):
    """ Create message for TypeError when value doesn't match expectation. """
    return "Expected {} but got {} ({})".format(
            exp_type, obs_value, type(obs_value))


if __name__ == '__main__':
    print(get_mod_doc(sys.argv[1]))
