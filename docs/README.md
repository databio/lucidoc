# lucidoc

`Lucidoc` automatically generates python package API documentation in Markdown from docstrings.

## Overview

Lucidoc aims to be a 


## Install


`lucidoc` is hosted on pypi. Install with:

```console
pip install --user lucidoc
```

Or, within active environment:
```console
pip install --upgrade lucidoc
```


## Usage

```console
lucidoc --help
version: 0.2
usage: lucidoc [-h] [-V] -P {rst} [--skip-module-docstring] [--inherited]
               [--whitelist WHITELIST | --blacklist BLACKLIST | --output-groups [OUTPUT_GROUPS [OUTPUT_GROUPS ...]]]
               [--outfile OUTFILE | --outfolder OUTFOLDER]
               pkgpath

Generate Markdown documentation for a module

positional arguments:
  pkgpath               Name/dotted path to package to document, i.e. what
                        you'd type as the target for an import statement

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -P {rst}, --parse {rst}
                        Name of parsing strategy for docstrings (default:
                        None)
  --skip-module-docstring
                        Indicate that module docstring should be omitted
                        (default: False)
  --inherited           Include inherited members (default: False)
  --whitelist WHITELIST
                        Names of objects to include in documentation (default:
                        None)
  --blacklist BLACKLIST
                        Names of objects to exclude from documentation
                        (default: None)
  --output-groups [OUTPUT_GROUPS [OUTPUT_GROUPS ...]]
                        Space-separated list of groups of objects to document
                        together; if used, this should be specified as:
                        --output-groups g1=obj1,obj2,... g2=objA,objB,...,
                        ...; i.e., spaces between groups and comma between
                        group members (default: None)
  --outfile OUTFILE     Path to file to which to write output (default: None)
  --outfolder OUTFOLDER
                        Path to folder in which to place output files; this
                        can only be used with --output-groups (default: None)
```


