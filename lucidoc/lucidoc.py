#!/usr/bin/env python
"""
Generate mkdocs-friendly API documentation for a Python package.

This program parses docstrings from objects defined in a Python package and
uses the information from those docstrings to generate mkdocs-friendly
documentation in Markdown format. Essentially, therefore, it generates
API documentation for the package.

"""

import argparse
from collections import defaultdict, Iterable
from functools import partial
import inspect
import itertools
import os
import pydoc
import sys

if sys.version_info < (3, 0):
    from inspect import getargspec as args_spec
else:
    from inspect import getfullargspec as args_spec

if sys.version_info < (3, 3):
    from collections import Mapping
else:
    from collections.abc import Mapping

from .helpers import *
from .docparse import get_parser, RST_KEY
from .doctags import MdTagRenderer
from .exceptions import LucidocError
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

    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--whitelist",
        help="Names of objects to include in documentation")
    selection.add_argument(
        "--blacklist",
        help="Names of objects to exclude from documentation")
    selection.add_argument(
        "--output-groups", nargs='*',
        help="Space-separated list of groups of objects to document together; "
             "if used, this should be specified as: "
             "--output-groups g1=obj1,obj2,... g2=objA,objB,..., ...; "
             "i.e., spaces between groups and comma between group members")

    output = parser.add_mutually_exclusive_group()
    output.add_argument(
        "--outfile",
        help="Path to file to which to write output")
    output.add_argument(
        "--outfolder",
        help="Path to folder in which to place output files; this can only be "
             "used with --output-groups")

    return parser.parse_args(cmdl)


def doc_module(mod, docstr_parser, render_tag,
               no_mod_docstr=False, include_inherited=False,
               retain=None, groups=None):
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
    :param callable retain: positive selection (on/by name) of doc targets
    :param Mapping[str, str | Iterable[str]] | Iterable[(str, str | Iterable[str])] groups:
        pairing of group name with either single target name or collection of target names
    :return str | Mapping[str, str]: Large block of Markdown-formatted
        documentation; alternatively, a mapping between group name and
        documentation block for the objects from that group
    :raise TypeError: if retention strategy is provided but is not callable
    """

    if retain and not hasattr(retain, "__call__"):
        raise TypeError("Object retention function must be callable")

    # Parameterize the object nature-specific documentation functions.
    doc_cls = partial(doc_class, docstr_parser=docstr_parser,
                      render_tag=render_tag, include_inherited=include_inherited)
    doc_fun = partial(doc_callable, docstr_parser=docstr_parser,
                      render_tag=render_tag)

    if groups:
        if isinstance(groups, Mapping):
            groups = list(groups.items())
        groups = [(g, [ns] if isinstance(ns, str) else ns) for g, ns in groups]
        try:
            declared = set(itertools.chain(*[ns for _, ns in groups]))
        except ValueError:
            print("ERROR: failed to parse target names from groups "
                  "declaration; ensure that groups are specified as a "
                  "mapping or as a collection of pairs.")
            raise
        if retain:
            print("Groups provided; only declared group members will be used "
                  "in documentation")
            use_obj = lambda name: retain(name) and name in declared
        else:
            use_obj = lambda name: name in declared
    else:
        declared = set()
        use_obj = retain or (lambda _: True)

    all_targets = [(n, o) for n, o in _get_targets(mod) if use_obj(n)]

    def collect_targets_by_name():
        m = defaultdict(list)
        for n, t in all_targets:
            m[n].append(t)
        res, reps = {}, []
        for n, ts in m.items():
            if len(ts) > 1:
                reps.append((n, ts))
            else:
                res[n] = ts[0]
        return res, reps

    all_targets, repeated = collect_targets_by_name()
    if repeated:
        raise LucidocError("Repeat target names:\n{}".format(
            "\n".join("{}: {}".format(n, ts) for n, ts in repeated)))

    missing_targets = declared - set(all_targets.keys())
    if missing_targets:
        print("WARNING: {} target(s) missing: {}".
              format(len(missing_targets), ", ".join(missing_targets)))

    # Header and module docstring
    output = [module_header.format(mod.__name__)]
    if mod.__doc__ and not no_mod_docstr:
        output.append(mod.__doc__)

    def build_doc_block(nt_pairs, prep):
        return list(itertools.chain(*[
            f(t) for _, t, f in prep(nt_pairs)]))

    def get_target_fun(t):
        if inspect.isfunction(t):
            return doc_fun
        elif inspect.isclass(t):
            return doc_cls

    if groups:
        def prepare_targets(named_targets):
            res = []
            for n, t in named_targets:
                if _unprotected(n):
                    f = get_target_fun(t)
                    f and res.append((n, t, f))
            return res
        chunk_groups = {g: [(n, all_targets[n]) for n in ns] for g, ns in groups}
        grouped_results = {g: build_doc_block(nt_pairs, prepare_targets)
                           for g, nt_pairs in chunk_groups.items()}
        return {g: "\n".join(map(str, output + chunks))
                for g, chunks in grouped_results.items()}
    else:
        def prepare_targets(named_targets):
            classes, functions = [], []
            for n, t in named_targets:
                if _unprotected(n):
                    if inspect.isfunction(t):
                        functions.append((n, t))
                    elif inspect.isclass(t):
                        classes.append((n, t))
            return [(n, t, doc_cls) for n, t in classes] + \
                   [(n, t, doc_fun) for n, t in functions]
        chunks = build_doc_block(all_targets.items(), prepare_targets)
        return "\n".join(map(str, output + chunks))


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
            raise LucidocError("Class docstring has a return value: {}".
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
            raise LucidocError("No name for object of {}; explicitly pass name "
                               "if documenting a property".format(type(f)))

    print("Processing function: {}".format(n))

    head = function_header.format(n.replace('_', '\\_'))

    signature = "```python\ndef {}{}\n```\n".format(
        n, "(self)" if isinstance(f, property) else
            pydoc.inspect.formatargspec(*args_spec(f)))

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
    nargs = len(args_spec(proc).args)
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


def _determine_retention_strategy(whitelist, blacklist, groups):
    """ Validate and determine how to implement specification of target seeking behavior. """
    if (whitelist and (groups or blacklist)) or \
            (blacklist and (whitelist or groups)) or \
            (groups and (blacklist or whitelist)):
        raise LucidocError("Only one retention strategy may be specified")
    if not whitelist and not blacklist and not groups:
        return lambda _: True
    if blacklist:
        return lambda n: n not in set(blacklist)
    # Reaching this point implies that either whitelist XOR blacklist is nonempty.
    pool = set(whitelist if whitelist else itertools.chain(*[names for _, names in groups]))
    def ret(n):
        return n in pool
    return ret


def _standardize_groups_type(groups):
    """ Ensure a consistent way of handling the type/structure of groups spec. """
    if not groups:
        return None
    if isinstance(groups, Mapping):
        return list(groups.items())
    elif isinstance(groups, Iterable) and not isinstance(groups, str):
        return groups
    else:
        raise TypeError("Groups specification must be mapping or collection of "
                        "pairs; got {} ({})".format(groups, type(groups)))


def run_lucidoc(pkg, parse_style, outfile=None, outfolder=None,
                no_mod_docstr=False, include_inherited=False,
                whitelist=None, blacklist=None, groups=None):
    """
    Discover docstrings and create package API documentation in Markdown.

    :param str pkg: name of the package to document
    :param str parse_style: key/name of parsing strategy to use
    :param str outfile: path to documentation output file
    :param str outfolder: path to folder in which to place docs output
    :param bool no_mod_docstr: whether to exclude the module-level docstring,
        if present
    :param bool include_inherited: whether to document inherited members
    :param Iterable[str] whitelist: names of doc targets to include
    :param Iterable[str] blacklist: names of doc targets to exclude
    :param Mapping[str, str | Iterable[str]] | Iterable[(str, str | Iterable[str])] groups:
        pairing of group name with either single target name or collection of target names
    :raise LucidocError: if passing both output file and output folder, or if
        passing output file and using groups
    """

    if outfile and outfolder:
        raise LucidocError("Cannot specify both output file and output folder")

    groups = _standardize_groups_type(groups)
    retain = _determine_retention_strategy(whitelist, blacklist, groups)

    if groups and outfile:
        raise LucidocError(
            "Cannot use output file with groups; to control output destination, "
            "consider output folder and each group names as filename.")

    try:
        sys.path.append(os.getcwd())
        # Attempt import
        pkg_obj = pydoc.safeimport(pkg)
        if pkg_obj is None:
            raise LucidocError(
                "ERROR -- Documentation target not found: {}".format(pkg))
    except pydoc.ErrorDuringImport:
        print("Failed to import '{}'".format(pkg))
        raise
    else:
        show_tag = MdTagRenderer()
        parse = get_parser(parse_style)
        doc_res = doc_module(
            pkg_obj, parse, show_tag, no_mod_docstr=no_mod_docstr,
            include_inherited=include_inherited, retain=retain, groups=groups)
        if groups:
            outfolder = expandpath(outfolder or os.getcwd())
            print("Base output folder: {}".format(outfolder))
            missing, invalid = [], []
            for g, _ in groups:
                try:
                    doc = doc_res[g]
                except KeyError:
                    missing.append(g)
                    continue
                base, ext = os.path.splitext(g)
                if ext:
                    if ext != ".md":
                        invalid.append(g)
                        continue
                    fn = g
                else:
                    fn = base + ".md"
                fp = os.path.join(outfolder, fn)
                print("Writing docs: {}".format(fp))
                with open(fp, 'w') as f:
                    f.write(doc)
            if missing:
                print("WARNING: missing output for {} group(s): {}".
                      format(len(missing), ", ".join(missing)))
            if invalid:
                print("WARNING: skipped writing {} group(s) on account of "
                      "illegal output file extension: {}".
                      format(len(invalid), ", ".join(invalid)))
            print("Done.")
        elif outfile:
            outdir = os.path.dirname(outfile)
            if outdir and not os.path.isdir(outdir):
                os.makedirs(outdir)
            print("Writing docs: {}".format(outfile))
            with open(outfile, 'w') as f:
                f.write(doc_res)
            print("Done.")
        else:
            print(doc_res)


def main():
    """ Main workflow """
    opts = _parse_args(sys.argv[1:])
    if opts.output_groups:
        groups = []
        seen = set()
        for gspec in opts.output_groups:
            try:
                group, name_spec = gspec.split("=")
            except ValueError:
                raise ValueError("Illegal output groups specification; "
                                 "please check usage with --help")
            if group in seen:
                raise ValueError("Duplicated group name: {}".format(group))
            seen.add(group)
            groups.append((group, name_spec.split(",")))
    else:
        groups = None
    run_lucidoc(opts.pkgpath, opts.parse,
                outfile=opts.outfile, outfolder=opts.outfolder,
                no_mod_docstr=opts.skip_module_docstring,
                include_inherited=opts.inherited,
                whitelist=opts.whitelist, blacklist=opts.blacklist, groups=groups)
    

if __name__ == '__main__':
    main()
