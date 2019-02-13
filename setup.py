#! /usr/bin/env python

import os
from setuptools import setup
import sys

PACKAGE = "oradocle"

# Additional keyword arguments for setup().
extra = {}

# Ordinary dependencies
DEPENDENCIES = []
with open("requirements.txt", 'r') as reqs_file:
    for line in reqs_file:
        if not line.strip():
            continue
        #DEPENDENCIES.append(line.split("=")[0].rstrip("<>"))
        DEPENDENCIES.append(line)

# 2to3
if sys.version_info >= (3, ):
    extra["use_2to3"] = True
extra["install_requires"] = DEPENDENCIES


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
    description="A ",
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="documentation, API, docs, mkdocs, autodoc",
    url="https://github.com/vreuter/{}/".format(PACKAGE),
    author=u"Vince Reuter",
    license="BSD2",
    entry_points={
        "console_scripts": [
            "{p} = {p}.{p}:main".format(p=PACKAGE)
        ],
    },
    include_package_data=True,
    **extra
)

