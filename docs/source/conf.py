# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

import SurVigilance

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, basedir)

project = "SurVigilance"
copyright = "2025, Raktim Mukhopadhyay, Marianthi Markatou"
author = "Raktim Mukhopadhyay, Marianthi Markatou"
release = SurVigilance.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.todo",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.githubpages",
    "nbsphinx",
    "sphinx.ext.intersphinx",
    "myst_parser",
]
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
    "html_image",
]
autosummary_generate = True


templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
# html_js_files = ["js/version_warning.js"]
strip_signature_backslash = True

# -- Options for Latex output -------------------------------------------------
latex_elements = {
    "extraclassoptions": "openany,oneside",
    "preamble": r"""
    \usepackage{amsmath, amssymb, amsfonts}
    \usepackage{fancyhdr}
    \makeatletter
    \fancypagestyle{normal}{
        \fancyhf{}
        \fancyfoot[R]{\py@HeaderFamily\thepage}
        \renewcommand{\headrulewidth}{0pt}
        \renewcommand{\footrulewidth}{0.4pt}
    }
    \makeatother
    """,
}
latex_documents = [
    (
        "index",
        "SurVigilance.tex",
        "SurVigilance",
        author,
        "manual",
    )
]


# Version warning to display on Read the Docs, this is taken from
# https://github.com/qucontrol/krotov/blob/969fc980346e6411903de854118c48c51208a810/docs/conf.py#L321
# Krotov Package
def setup(app):
    app.add_js_file("js/version_warning.js")  # Custom JS file for version warning
