<script>
document.addEventListener('DOMContentLoaded', (event) => {
  document.querySelectorAll('h3 code').forEach((block) => {
    hljs.highlightBlock(block);
  });
});
</script>

<style>
h3 .content { 
    padding-left: 22px;
    text-indent: -15px;
 }
h3 .hljs .content {
    padding-left: 20px;
    margin-left: 0px;
    text-indent: -15px;
    martin-bottom: 0px;
}
h4 .content, table .content, p .content, li .content { margin-left: 30px; }
h4 .content { 
    font-style: italic;
    font-size: 1em;
    margin-bottom: 0px;
}

</style>


# Package `lucidoc` Documentation

## <a name="DocTag"></a> Class `DocTag`
Representation of a tag within a docstring


```python
def __init__(self, typename, description)
```

Initialize self.  See help(type(self)) for accurate signature.



```python
def description(self)
```

Described value to which this tag pertains
#### Returns:

- `str`:  description of value being tagged




```python
def typename(self)
```

Get the name of the type(s) associated with the tag
#### Returns:

- `str`:  Text of either single type name or union of several




## <a name="DocstringParser"></a> Class `DocstringParser`
Entity responsible for parsing docstrings


```python
def description(self, ds)
```

Parse the description portion of a docstring.
#### Parameters:

- `ds` (`str`):  docstring from which to parse description


#### Returns:

- `str`:  description portion of docstring




```python
def params(self, ds)
```

Parse parameter tags from docstring.
#### Parameters:

- `ds` (`str`):  docstring from which to parse parameter tags


#### Returns:

- `Iterable[lucidoc.ParTag]`:  (possibly empty) collection ofparameter tags parsed from the given docstring




```python
def raises(self, ds)
```

Parse parameter tags from docstring.
#### Parameters:

- `ds` (`str`):  docstring from which to parse result tag


#### Returns:

- `Iterable[lucidoc.ErrTag]`:  (possibly empty) collection ofparameter tags parsed from the given docstring




```python
def returns(self, ds)
```

Parse parameter tags from docstring.
#### Parameters:

- `ds` (`str`):  docstring from which to parse result tag


#### Returns:

- `lucidoc.RetTag | NoneType`:  (possibly empty) collection ofparameter tags parsed from the given docstring




## <a name="DocstringStyler"></a> Class `DocstringStyler`
How to style/render docstrings


## <a name="ErrTag"></a> Class `ErrTag`
Tag for type and description of a potential Exception


```python
def description(self)
```

Described value to which this tag pertains
#### Returns:

- `str`:  description of value being tagged




```python
def typename(self)
```

Get the name of the type(s) associated with the tag
#### Returns:

- `str`:  Text of either single type name or union of several




## <a name="LucidocError"></a> Class `LucidocError`
Base error type for this package


## <a name="MdTagRenderer"></a> Class `MdTagRenderer`
Render tag for Markdown


## <a name="ParTag"></a> Class `ParTag`
Representation of a parameter tag in docstring


```python
def __init__(self, name, typename, description)
```

Create a parameter tag with a name, typename, and description.
#### Parameters:

- `name` (`str`):  the formal parameter name
- `typename` (``):  text describing valid argument types
- `description` (``):  detail about the parameter and/or accepted args




```python
def description(self)
```

Described value to which this tag pertains
#### Returns:

- `str`:  description of value being tagged




```python
def name(self)
```

Get the parameter name.
#### Returns:

- `str`:  The parameter name for this tag




```python
def typename(self)
```

Get the name of the type(s) associated with the tag
#### Returns:

- `str`:  Text of either single type name or union of several




## <a name="ParsedDocstringResult"></a> Class `ParsedDocstringResult`
ParsedDocstringResult(doc, desc, params, returns, raises, examples)


```python
def desc(self)
```

Alias for field number 1



```python
def doc(self)
```

Alias for field number 0



```python
def examples(self)
```

Alias for field number 5



```python
def params(self)
```

Alias for field number 2



```python
def raises(self)
```

Alias for field number 4



```python
def returns(self)
```

Alias for field number 3



## <a name="PycodeDocstringStyler"></a> Class `PycodeDocstringStyler`
Style/render docstring by wrapping it in Python code block fences.


## <a name="RetTag"></a> Class `RetTag`
Tag for type and description of return value


```python
def description(self)
```

Described value to which this tag pertains
#### Returns:

- `str`:  description of value being tagged




```python
def typename(self)
```

Get the name of the type(s) associated with the tag
#### Returns:

- `str`:  Text of either single type name or union of several




## <a name="RstDocstringParser"></a> Class `RstDocstringParser`
Parser for ReStructured text docstrings.


```python
def __init__(self)
```

Set the most recently seen docstring parse result to null.



```python
def description(self, ds)
```

Parse the description portion of a docstring.
#### Parameters:

- `ds` (`str`):  docstring from which to parse description


#### Returns:

- `str`:  description portion of docstring




```python
def examples(self, ds)
```

Get the code example text from a docstring.
#### Parameters:

- `ds` (`str`):  docstring from which to parse example


#### Returns:

- `str`:  code example text from docstring




```python
def params(self, ds)
```

Parse parameter tags from docstring.
#### Parameters:

- `ds` (`str`):  docstring from which to parse parameter tags


#### Returns:

- `Iterable[lucidoc.ParTag]`:  (possibly empty) collection ofparameter tags parsed from the given docstring




```python
def raises(self, ds)
```

Parse parameter tags from docstring.
#### Parameters:

- `ds` (`str`):  docstring from which to parse result tag


#### Returns:

- `Iterable[lucidoc.ErrTag]`:  (possibly empty) collection ofparameter tags parsed from the given docstring




```python
def returns(self, ds)
```

Parse parameter tags from docstring.
#### Parameters:

- `ds` (`str`):  docstring from which to parse result tag


#### Returns:

- `lucidoc.RetTag | NoneType`:  (possibly empty) collection ofparameter tags parsed from the given docstring




## <a name="TagRenderer"></a> Class `TagRenderer`
Strategy for rendering a tag.


```python
def doc_callable(f, docstr_parser, render_tag, name=None)
```

For single function get text components for Markdown documentation.
#### Parameters:

- `f` (`callable | property`):  function or property to document
- `docstr_parser` (`lucidoc.DocstringParser`):  How to parse a docstring.
- `render_tag` (`callable(lucidoc.DocTag) -> str`):  how to render anindividual tag from a docstring. The implementation in the object passed as an argument should handle each type of DocTag that may be passed as an argument when this object is called.
- `name` (`str`):  name of object being documented; pass directly for prop.


#### Returns:

- `list[str]`:  text chunks constituting Markdown documentation forsingle function.




```python
def doc_class(cls, docstr_parser, render_tag, include_inherited, nested=False)
```

For single class definition, get text components for Markdown documentation.
#### Parameters:

- `cls` (`class`):  class to document with Markdown
- `docstr_parser` (`lucidoc.DocstringParser`):  How to parse a docstring.
- `render_tag` (`callable(lucidoc.DocTag) -> str`):  how to render anindividual tag from a docstring. The implementation in the object passed as an argument should handle each type of DocTag that may be passed as an argument when this object is called.
- `include_inherited` (`bool`):  include inherited members
- `nested` (`bool`):  whether the given target is nested within another class


#### Returns:

- `list[str]`:  text chunks constituting Markdown documentation forsingle class definition.




```python
def doc_module(mod, docstr_parser, render_tag, no_mod_docstr=False, include_inherited=False, retain=None, groups=None, omit_meta=False)
```

Get large block of Markdown-formatted documentation of a module
#### Parameters:

- `mod` (`module`):  module to document in Markdown.
- `docstr_parser` (`lucidoc.DocstringParser`):  how to parse a docstring.
- `render_tag` (`callable(lucidoc.DocTag) -> str`):  how to render a tagparsed from a docstring; the argument should be total. In other words, each potential type of tag that may be passed to it as an argument should be accounted for in the implementation.
- `no_mod_docstr` (`bool`):  skip module-level docstring
- `include_inherited` (`bool`):  include inherited members
- `retain` (`callable`):  positive selection (on/by name) of doc targets
- `groups` (`Mapping[str, str | Iterable[str]] | Iterable[(str, str | Iterable[str])]`): pairing of group name with either single target name or collection of target names
- `omit_meta` (`bool`):  whether the version metadata for documentationtarget and for this package should be omitted from the documentation that's created


#### Returns:

- `str | Mapping[str, str]`:  Large block of Markdown-formatteddocumentation; alternatively, a mapping between group name and documentation block for the objects from that group


#### Raises:

- `TypeError`:  if retention strategy is provided but is not callable




```python
def get_parser(name)
```

Get a docstring parsing strategy.
#### Parameters:

- `name` (`str`):  Key for a parsing strategy.


#### Returns:

- `lucidoc.DocstringParser`:  The parser to which the given name ismapped.


#### Raises:

- `lucidoc.UnknownParserError`:  If given a nonempty name that's notmapped to a parser.




```python
def get_styler(name)
```

Get a docstring styling strategy.
#### Parameters:

- `name` (`str`):  name/key of desired styling strategy


#### Returns:

- `lucidoc.DocstringStyler`:  styler to which given name is mapped.


#### Raises:

- `lucidoc.UnknownStylerError`:  if given a nonempty name that's notmapped to a styler.




```python
def run_lucidoc(pkg, parse_style, outfile=None, outfolder=None, no_mod_docstr=False, include_inherited=False, whitelist=None, blacklist=None, groups=None, omit_meta=False, **log_kwargs)
```

Discover docstrings and create package API documentation in Markdown.
#### Parameters:

- `pkg` (`str`):  name of the package to document
- `parse_style` (`str`):  key/name of parsing strategy to use
- `outfile` (`str`):  path to documentation output file
- `outfolder` (`str`):  path to folder in which to place docs output
- `no_mod_docstr` (`bool`):  whether to exclude the module-level docstring,if present
- `include_inherited` (`bool`):  whether to document inherited members
- `whitelist` (`Iterable[str]`):  names of doc targets to include
- `blacklist` (`Iterable[str]`):  names of doc targets to exclude
- `groups` (`Mapping[str, str | Iterable[str]] | Iterable[(str, str | Iterable[str])]`): pairing of group name with either single target name or collection of target names
- `omit_meta` (`bool`):  whether the version metadata for documentationtarget and for this package should be omitted from the documentation that's created


#### Raises:

- `TypeError`:  if passing an argument to whitelist or blacklist that'snot a non-string collection, or if passing an argument to groups in which a group's names isn't a non-string collection
- `LucidocError`:  if passing both output file and output folder, or ifpassing output file and using groups; or if using more than one of whitelist, blacklist, and groups
- `pydoc.ErrorDuringImport`:  if the argument to the package parameter(pkg) cannot be imported







*Version Information: `lucidoc` v0.4.2, generated by `lucidoc` v0.4.2*