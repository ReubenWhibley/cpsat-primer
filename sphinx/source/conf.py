# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath('../../evaluations'))

project = 'cp-sat primer'
copyright = '2023, Dominik Krupke (TU Braunschweig, IBR, Algorithms Group)'
author = 'Dominik Krupke (TU Braunschweig, IBR, Algorithms Group)'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser',
              'sphinx.ext.viewcode',
              'sphinx.ext.autodoc',
             ]

templates_path = ['_templates']
exclude_patterns = []
source_suffix = ['.md']


master_doc = 'index'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'


