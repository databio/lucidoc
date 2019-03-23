# Package lucidoc Documentation

## Class DocTag
Representation of a tag within a docstring


### description
Described value to which this tag pertains
```python
def description:
```

**Returns:**

`str`:  description of value being tagged




### typename
Get the name of the type(s) associated with the tag
```python
def typename:
```

**Returns:**

`str`:  Text of either single type name or union of several




## Class DocstringParser
Entity responsible for parsing docstrings


## Class DocstringStyler
How to style/render docstrings


## Class ErrTag
Tag for type and description of a potential Exception


### description
Described value to which this tag pertains
```python
def description:
```

**Returns:**

`str`:  description of value being tagged




### typename
Get the name of the type(s) associated with the tag
```python
def typename:
```

**Returns:**

`str`:  Text of either single type name or union of several




## Class MdTagRenderer
Render tag for Markdown


## Class ParTag
Representation of a parameter tag in docstring


### description
Described value to which this tag pertains
```python
def description:
```

**Returns:**

`str`:  description of value being tagged




### name
Get the parameter name.
```python
def name:
```

**Returns:**

`str`:  The parameter name for this tag




### typename
Get the name of the type(s) associated with the tag
```python
def typename:
```

**Returns:**

`str`:  Text of either single type name or union of several




## Class ParsedDocstringResult
ParsedDocstringResult(doc, desc, params, returns, raises, examples)


### desc
Alias for field number 1
```python
def desc:
```




### doc
Alias for field number 0
```python
def doc:
```




### examples
Alias for field number 5
```python
def examples:
```




### params
Alias for field number 2
```python
def params:
```




### raises
Alias for field number 4
```python
def raises:
```




### returns
Alias for field number 3
```python
def returns:
```




## Class PycodeDocstringStyler
Style/render docstring by wrapping it in Python code block fences.


## Class RetTag
Tag for type and description of return value


### description
Described value to which this tag pertains
```python
def description:
```

**Returns:**

`str`:  description of value being tagged




### typename
Get the name of the type(s) associated with the tag
```python
def typename:
```

**Returns:**

`str`:  Text of either single type name or union of several




## Class RstDocstringParser
Parser for ReStructured text docstrings.


## Class TagRenderer
Strategy for rendering a tag.


## Class lucidocError
Base error type for this package


### doc\_callable
For single function get text components for Markdown documentation.
```python
def doc_callable(f, docstr_parser, render_tag, name=None):
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
def doc_class(cls, docstr_parser, render_tag, include_inherited):
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
def doc_module(mod, docstr_parser, render_tag, no_mod_docstr=False, include_inherited=False):
```

**Parameters:**

- `mod` -- `module`:  module to document in Markdown.
- `docstr_parser` -- `lucidoc.DocstringParser`:  how to parse a docstring.
- `render_tag` -- `callable(lucidoc.DocTag) -> str`:  how to render a tagparsed from a docstring; the argument should be total. In other words, each potential type of tag that may be passed to it as an argument should be accounted for in the implementation.
- `no_mod_docstr` -- `bool`:  skip module-level docstring
- `include_inherited` -- `bool`:  include inherited members


**Returns:**

`str`:  Large block of Markdown-formatted documentation of a module.




### get\_parser
Get a docstring parsing strategy.
```python
def get_parser(name):
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
def get_styler(name):
```

**Parameters:**

- `name` -- `str`:  name/key of desired styling strategy


**Returns:**

`lucidoc.DocstringStyler`:  styler to which given name is mapped.


**Raises:**

- `lucidoc.UnknownStylerError`:  if given a nonempty name that's notmapped to a styler.




### run\_lucidoc
```python
def run_lucidoc(pkg, parse_style, outfile, no_mod_docstr=False, include_inherited=False):
```


