# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))
if not (Path(__file__).parent / "_static").exists():
    os.mkdir("_static")

with open("../toppy/client.py") as client:
    version_regex = re.compile(r"__version__ = \"(?P<v>[0-9]\.[0-9]{1,2}\.[0-9]+)(-(pre|alpha|beta)\.[0-9]+)?\"")
    ct = client.read()
    __version__ = version_regex.search(ct).group("v")

# -- Project information -----------------------------------------------------

project = "top.py"
copyright = "2021, DragDev Studios"
author = "DragDev Studios"
version = __version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.duration", "sphinx.ext.intersphinx", "sphinx_rtd_dark_mode"]

intersphinx_mapping = {"discord": (f"https://discordpy.readthedocs.io/en/stable", None)}
extlinks = {
    "issue": ("https://github.com/dragdev-studios/top.py/issues/%s", "GH-"),
}
default_dark_mode = True
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
