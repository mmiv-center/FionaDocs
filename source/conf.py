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
import sys

sys.path.insert(0, os.path.abspath('.'))

# -- Our helpers --------------------------------------------------------------
# Functions in config_loader.py module to load config/links.json file


# Import log_files
from helpers import load_config, generate_substitutions

# Load configurations and generate substitutions
config = load_config()
rst_prolog = generate_substitutions(config)

#print("*******************")
# print(rst_prolog)
#print("*******************")



# -- Project information for HTML ------------------------------------------

project = 'Fiona Documentation'
copyright = '2025, Hauke Bartsch'
version = '0.1'


#institution = "Haukeland University Hospital, Department of Radiology,\n"
#center = "Mohn Medical Imaging and Visualization Centre,\n"
#authors = "Hauke Bartsch, Marek Kociński, Line Nigardsøy Lie"
#author = f"{institution}, {center} {authors} blablabla"





# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

# Allows to enbeded Mermaid graphs into the documentation
extensions = ['sphinxcontrib.mermaid']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']




# ----------- 2025.07.28 - mk --- add latex setup ----------------------------
# Mermaid configuration
mermaid_output_format = 'png'  # lub 'svg'
mermaid_cmd = '/home/marek/.npm-global/bin/mmdc'
mermaid_params = [
    '--theme', 'neutral',
    '--backgroundColor', 'transparent',
    '--width', '1200',
    '--height', '800'
]

# For LaTeX - convert to images
mermaid_init_js = """
{
    "theme": "neutral",
    "themeVariables": {
        "primaryColor": "#ff0000"
    }
}
"""

# LaTeX front page, load from a tex file
with open('titlepage.tex', 'r', encoding='utf-8') as f:
    titlepage_content = f.read()

latex_elements = {
   'preamble': r'''
        \usepackage{graphicx}
        ''',
    'maketitle': titlepage_content,
}

# Files that must be copied manually or semimanually
latex_additional_files = ['_static/leaf10.png']

# -----------------------------------------------------------------------------

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []



# -- Autodoc configuration (by mk) ------------------------------------------
autodoc_default_options = {
       # 'members': False,
       # 'member-order': 'bysource',
       # 'special-members': False,
       # 'undoc-members': False,
       # 'exclude-members': '__weakref__'
        }


# Temporary Ignore file compilaton due to import errors
autodoc_mock_imports = []



# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'navigation_depth': -1,  # Shows all levels
    'collapse_navigation': False,  # Disables menu collapsing
    'sticky_navigation': True,  # Menu stays in place when scrolling
    'includehidden': True,  # Shows hidden elements
    'titles_only': False,  # Shows not only titles
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# Add CSS description
html_css_files = ['custom.css',]

# Add non-statndad JavaScript
html_js_files = ['custom.js',]


