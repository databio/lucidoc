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


__all__ = ["getmarkdown", "getclasses", "getfunctions", "generatedocs"]


def getmarkdown(module):
    """
    Get large block of Markdown-formatted documentation of a module

    Parameters
    ----------
    module : module
        Module to document in Markdown.

    Returns
    -------
    str
        Large block of Markdown-formatted documentation of a module.

    """
    output = [module_header.format(module.__name__)]
    if module.__doc__:
        output.append(module.__doc__)
    try:
        names = module.__all__
    except AttributeError:
        output.extend(getclasses(module))
        output.extend(getfunctions(module))
    else:
        objs, missing = [], []
        for n in names:
            try:
                objs.append((n, getattr(module, n)))
            except AttributeError:
                missing.append(n)
        if missing:
            raise AttributeError("Module is missing declared export(s): {}".format(", ".join(missing)))
        unprocessed = []
        for n, o in objs:
            if inspect.isclass(o):
                doc = _process_class(o)
            elif inspect.isfunction(o):
                doc = _process_function(o)
            else:
                unprocessed.append(n)
                continue
            output.append(doc)
        if unprocessed:
            print("WARNING: {} unprocessed exported object(s) from module "
                  "{}:\n{}".format(len(unprocessed), module.__name__,
                                   "\n".join(unprocessed)))
    #output.extend(getclasses(module))
    return "\n".join(str(x) for x in output)


def getclasses(item):
    """
    Get Markdown documentation chunks for each class in the given object.

    Parameters
    ----------
    item : module
        Module in which to find classes to document with Markdown

    Returns
    -------
    list of str
        Collection of Markdown documentation chunks covering each (unprotected)
        class defined in the given module.

    """
    output = list()
    for cl in pydoc.inspect.getmembers(item, pydoc.inspect.isclass):
        if cl[0] != "__class__" and not cl[0].startswith("_"):
            # Consider anything that starts with _ private
            # and don't document it
            output.append(class_header.format(cl[0]))
            # Get the docstring
            output.append(pydoc.inspect.getdoc(cl[1]))
            # Get the functions
            output.extend(getfunctions(cl[1]))
            # Recurse into any subclasses
            output.extend(getclasses(cl[1]))
            output.append('\n')
    return output


def getfunctions(item):
    """
    Get Markdown documentation chunks for each function in the given object.

    Parameters
    ----------
    item : module or class
        Module or class in which to find classes to document with Markdown.

    Returns
    -------
    list of str
        Collection of Markdown documentation chunks covering each (unprotected)
        function defined in the given object.

    """
    output = list()
    for func in pydoc.inspect.getmembers(item, pydoc.inspect.ismethod):
        if func[0].startswith('_') and func[0] != '__init__':
            continue
        output.append(function_header.format(func[0].replace('_', '\\_')))
        # Get the signature.
        output.append('```py\n')
        output.append('def %s%s\n' % (func[0], pydoc.inspect.formatargspec(*pydoc.inspect.getargspec(func[1]))))
        output.append('```\n')
        # Get the docstring.
        if pydoc.inspect.getdoc(func[1]):
            output.append('\n')
            output.append(pydoc.inspect.getdoc(func[1]))
        output.append('\n')
    return output


def generatedocs(module):
    """
    Generate Markdown documentation for classes and functions in a module.

    Parameters
    ----------
    module : module
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
        mod = pydoc.safeimport(module)
        if mod is None:
            print("Module not found")
        
        # Module imported correctly, let's create the docs
        return getmarkdown(mod)
    except pydoc.ErrorDuringImport as e:
        print("Error while trying to import " + module)


def _process_class(cl):
    """
    For single class definition, get text components for Markdown documentation.

    Parameters
    ----------
    cl : class
        Class to document with Markdown

    Returns
    -------
    list of str
        Text chunks constituting Markdown documentation for single class
        definition.

    """
    cls = cl[1]
    cls_doc = [class_header.format(cl[0]), pydoc.inspect.getdoc(cls)]
    func_docs = getfunctions(cls)
    subcls_docs = getclasses(cls)
    return cls_doc + func_docs + subcls_docs


def _process_function(f):
    """
    For single function get text components for Markdown documentation.

    Parameters
    ----------
    f : function
        Function to document with Markdown

    Returns
    -------
    list of str
        Text chunks constituting Markdown documentation for single function.

    """
    if not inspect.isfunction(f):
        raise TypeError("Expected function but got {}".format(type(f)))


if __name__ == '__main__':
    print(generatedocs(sys.argv[1]))
