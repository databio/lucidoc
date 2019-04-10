#! /usr/bin/env python

import os
from setuptools import setup
import sys

PACKAGE = "lucidoc"
REQDIR = "requirements"


def read_reqs(reqs_name):
    with open(os.path.join(REQDIR, "requirements-{}.txt".format(reqs_name)), 'r') as f:
        return [l.strip() for l in f if l.strip()]


# Additional keyword arguments for setup().
extra = {"install_requires": read_reqs("all")}
if sys.version_info >= (3, ):
    extra["use_2to3"] = True


def read_version(vers_file_path):
    with open(vers_file_path, 'r') as f:
        return f.readline().split()[-1].strip("\"'\n")


# Handle the pypi README formatting.
try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError, OSError, RuntimeError):
    long_description = open('README.md').read()

setup(
    name=PACKAGE,
    packages=[PACKAGE],
    version=read_version("{}/_version.py".format(PACKAGE)),
    description="API documentation in Markdown",
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="documentation, API, docs, mkdocs, autodoc",
    url="https://github.com/databio/{}/".format(PACKAGE),
    author=u"Vince Reuter",
    license="BSD2",
    entry_points={
        "console_scripts": [
            "{prog} = {pkg}.{prog}:main".format(pkg=PACKAGE, prog="lucidoc")
        ],
    },
    include_package_data=True,
    test_suite="tests",
    tests_require=read_reqs("dev"),
    setup_requires=(["pytest-runner"] if {"test", "pytest", "ptr"} & set(sys.argv) else []),
    **extra
)
