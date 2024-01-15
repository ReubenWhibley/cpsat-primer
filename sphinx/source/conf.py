# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath('../../chapters'))

current_dir = os.path.dirname(__file__)
chapters_dir = os.path.join(current_dir,'..','..','chapters')
chapter0 = os.path.join(chapters_dir, '00_introduction.md')
chapter1 = os.path.join(chapters_dir, '01_installation.md')
chapter2 = os.path.join(chapters_dir, '02_example.md')
chapter3 = os.path.join(chapters_dir, '03_modelling.md')
chapter4 = os.path.join(chapters_dir, '04_parameters.md')
chapter5 = os.path.join(chapters_dir, '05_how-does-it-work.md')
chapter6 = os.path.join(chapters_dir, '06_benchmarking-your-model.md')
chapter7 = os.path.join(chapters_dir, '07_large-neighborhood-search.md')
 
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


md_files = [
    chapter0,
    chapter1,
    chapter2,
    chapter3,
    chapter4,
    chapter5,
    chapter6,
    chapter7
]

master_doc = 'index'

# Concatenate all specified .md files into one README.md file
with open('../../README.md', 'w') as readme_file:
    for md_file in md_files:
        with open(md_file, 'r') as chapter_file:
            readme_file.write(chapter_file.read())

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'


