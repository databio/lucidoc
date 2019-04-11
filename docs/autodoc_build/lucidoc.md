# Package lucidoc Documentation

## Class DocTag
Representation of a tag within a docstring


### description
Described value to which this tag pertains
```python
def description(self)
```

**Returns:**

`str`:  description of value being tagged




### typename
Get the name of the type(s) associated with the tag
```python
def typename(self)
```

**Returns:**

`str`:  Text of either single type name or union of several




## Class DocstringParser
Entity responsible for parsing docstrings


### description
Parse the description portion of a docstring.
```python
def description(self, ds)
```

**Parameters:**

- `ds` -- `str`:  docstring from which to parse description


**Returns:**

`str`:  description portion of docstring




### params
Parse parameter tags from docstring.
```python
def params(self, ds)
```

**Parameters:**

- `ds` -- `str`:  docstring from which to parse parameter tags


**Returns:**

`Iterable[lucidoc.ParTag]`:  (possibly empty) collection ofparameter tags parsed from the given docstring




### raises
Parse parameter tags from docstring.
```python
def raises(self, ds)
```

**Parameters:**

- `ds` -- `str`:  docstring from which to parse result tag


**Returns:**

`Iterable[lucidoc.ErrTag]`:  (possibly empty) collection ofparameter tags parsed from the given docstring




### returns
Parse parameter tags from docstring.
```python
def returns(self, ds)
```

**Parameters:**

- `ds` -- `str`:  docstring from which to parse result tag


**Returns:**

`lucidoc.RetTag | NoneType`:  (possibly empty) collection ofparameter tags parsed from the given docstring




## Class DocstringStyler
How to style/render docstrings


## Class ErrTag
Tag for type and description of a potential Exception


### description
Described value to which this tag pertains
```python
def description(self)
```

**Returns:**

`str`:  description of value being tagged




### typename
Get the name of the type(s) associated with the tag
```python
def typename(self)
```

**Returns:**

`str`:  Text of either single type name or union of several




## Class LucidocError
Base error type for this package


## Class MdTagRenderer
Render tag for Markdown


## Class ParTag
Representation of a parameter tag in docstring


### description
Described value to which this tag pertains
```python
def description(self)
```

**Returns:**

`str`:  description of value being tagged




### name
Get the parameter name.
```python
def name(self)
```

**Returns:**

`str`:  The parameter name for this tag




### typename
Get the name of the type(s) associated with the tag
```python
def typename(self)
```

**Returns:**

`str`:  Text of either single type name or union of several




## Class ParsedDocstringResult
ParsedDocstringResult(doc, desc, params, returns, raises, examples)


### desc
Alias for field number 1
```python
def desc(self)
```




### doc
Alias for field number 0
```python
def doc(self)
```




### examples
Alias for field number 5
```python
def examples(self)
```




### params
Alias for field number 2
```python
def params(self)
```




### raises
Alias for field number 4
```python
def raises(self)
```




### returns
Alias for field number 3
```python
def returns(self)
```




## Class PycodeDocstringStyler
Style/render docstring by wrapping it in Python code block fences.


## Class RetTag
Tag for type and description of return value


### description
Described value to which this tag pertains
```python
def description(self)
```

**Returns:**

`str`:  description of value being tagged




### typename
Get the name of the type(s) associated with the tag
```python
def typename(self)
```

**Returns:**

`str`:  Text of either single type name or union of several




## Class RstDocstringParser
Parser for ReStructured text docstrings.


### description
Parse the description portion of a docstring.
```python
def description(self, ds)
```

**Parameters:**

- `ds` -- `str`:  docstring from which to parse description


**Returns:**

`str`:  description portion of docstring




### examples
Get the code example text from a docstring.
```python
def examples(self, ds)
```

**Parameters:**

- `ds` -- `str`:  docstring from which to parse example


**Returns:**

`str`:  code example text from docstring




### params
Parse parameter tags from docstring.
```python
def params(self, ds)
```

**Parameters:**

- `ds` -- `str`:  docstring from which to parse parameter tags


**Returns:**

`Iterable[lucidoc.ParTag]`:  (possibly empty) collection ofparameter tags parsed from the given docstring




### raises
Parse parameter tags from docstring.
```python
def raises(self, ds)
```

**Parameters:**

- `ds` -- `str`:  docstring from which to parse result tag


**Returns:**

`Iterable[lucidoc.ErrTag]`:  (possibly empty) collection ofparameter tags parsed from the given docstring




### returns
Parse parameter tags from docstring.
```python
def returns(self, ds)
```

**Parameters:**

- `ds` -- `str`:  docstring from which to parse result tag


**Returns:**

`lucidoc.RetTag | NoneType`:  (possibly empty) collection ofparameter tags parsed from the given docstring




## Class TagRenderer
Strategy for rendering a tag.


### doc\_callable
For single function get text components for Markdown documentation.
```python
def doc_callable(f, docstr_parser, render_tag, name=None)
```

**Parameters:**

- `f` -- `callable | property`:  function or property to document
- `docstr_parser` -- `lucidoc.DocstringParser`:  How to parse a docstring.
- `render_tag` -- `callable(lucidoc.DocTag) -> str`:  how to render anindividual tag from a docstring. The implementation in the object passed as an argument should handle each type of DocTag that may be passed as an argument when this object is called.
- `name` -- `str`:  name of object being documented; pass directly for prop.


**Returns:**

`list[str]`:  text chunks constituting Markdown documentation forsingle function.




### doc\_class
For single class definition, get text components for Markdown documentation.
```python
def doc_class(cls, docstr_parser, render_tag, include_inherited)
```

**Parameters:**

- `cls` -- `class`:  class to document with Markdown
- `docstr_parser` -- `lucidoc.DocstringParser`:  How to parse a docstring.
- `render_tag` -- `callable(lucidoc.DocTag) -> str`:  how to render anindividual tag from a docstring. The implementation in the object passed as an argument should handle each type of DocTag that may be passed as an argument when this object is called.
- `include_inherited` -- `bool`:  include inherited members


**Returns:**

`list[str]`:  text chunks constituting Markdown documentation forsingle class definition.




### doc\_module
Get large block of Markdown-formatted documentation of a module
```python
def doc_module(mod, docstr_parser, render_tag, no_mod_docstr=False, include_inherited=False, retain=None, groups=None, omit_meta=False)
```

**Parameters:**

- `mod` -- `module`:  module to document in Markdown.
- `docstr_parser` -- `lucidoc.DocstringParser`:  how to parse a docstring.
- `render_tag` -- `callable(lucidoc.DocTag) -> str`:  how to render a tagparsed from a docstring; the argument should be total. In other words, each potential type of tag that may be passed to it as an argument should be accounted for in the implementation.
- `no_mod_docstr` -- `bool`:  skip module-level docstring
- `include_inherited` -- `bool`:  include inherited members
- `retain` -- `callable`:  positive selection (on/by name) of doc targets
- `groups` -- `Mapping[str, str | Iterable[str]] | Iterable[(str, str | Iterable[str])]`: pairing of group name with either single target name or collection of target names
- `omit_meta` -- `bool`:  whether the version metadata for documentationtarget and for this package should be omitted from the documentation that's created


**Returns:**

`str | Mapping[str, str]`:  Large block of Markdown-formatteddocumentation; alternatively, a mapping between group name and documentation block for the objects from that group


**Raises:**

- `TypeError`:  if retention strategy is provided but is not callable




### get\_parser
Get a docstring parsing strategy.
```python
def get_parser(name)
```

**Parameters:**

- `name` -- `str`:  Key for a parsing strategy.


**Returns:**

`lucidoc.DocstringParser`:  The parser to which the given name ismapped.


**Raises:**

- `lucidoc.UnknownParserError`:  If given a nonempty name that's notmapped to a parser.




### get\_styler
Get a docstring styling strategy.
```python
def get_styler(name)
```

**Parameters:**

- `name` -- `str`:  name/key of desired styling strategy


**Returns:**

`lucidoc.DocstringStyler`:  styler to which given name is mapped.


**Raises:**

- `lucidoc.UnknownStylerError`:  if given a nonempty name that's notmapped to a styler.




### run\_lucidoc
Discover docstrings and create package API documentation in Markdown.
```python
def run_lucidoc(pkg, parse_style, outfile=None, outfolder=None, no_mod_docstr=False, include_inherited=False, whitelist=None, blacklist=None, groups=None, omit_meta=False, **log_kwargs)
```

**Parameters:**

- `pkg` -- `str`:  name of the package to document
- `parse_style` -- `str`:  key/name of parsing strategy to use
- `outfile` -- `str`:  path to documentation output file
- `outfolder` -- `str`:  path to folder in which to place docs output
- `no_mod_docstr` -- `bool`:  whether to exclude the module-level docstring,if present
- `include_inherited` -- `bool`:  whether to document inherited members
- `whitelist` -- `Iterable[str]`:  names of doc targets to include
- `blacklist` -- `Iterable[str]`:  names of doc targets to exclude
- `groups` -- `Mapping[str, str | Iterable[str]] | Iterable[(str, str | Iterable[str])]`: pairing of group name with either single target name or collection of target names
- `omit_meta` -- `bool`:  whether the version metadata for documentationtarget and for this package should be omitted from the documentation that's created


**Raises:**

- `TypeError`:  if passing an argument to whitelist or blacklist that'snot a non-string collection, or if passing an argument to groups in which a group's names isn't a non-string collection
- `LucidocError`:  if passing both output file and output folder, or ifpassing output file and using groups; or if using more than one of whitelist, blacklist, and groups
- `pydoc.ErrorDuringImport`:  if the argument to the package parameter(pkg) cannot be imported





**Version Information**: `lucidoc` v0.3dev, generated by `lucidoc` v0.3dev