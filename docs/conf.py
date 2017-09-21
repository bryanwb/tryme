# -*- coding: utf-8 -*-
#
# Tryme documentation build configuration file.
import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, PROJECT_DIR)

import tryme

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.viewcode',
]

source_suffix = '.rst'

master_doc = 'index'

project = u'Tryme'
copyright = u'2017, Bryan W. Berry'

version = tryme.VERSION
release = tryme.VERSION

exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_theme = 'agogo'
# use RTD new theme
RTD_NEW_THEME = True

htmlhelp_basename = 'Trymedoc'

latex_documents = [
    ('index', 'Tryme.tex', u'Tryme Documentation',
     u'Bryan W. Berry', 'manual'),
]

man_pages = [
    ('index', 'tryme', u'Tryme Documentation',
     [u'Bryan W. Berry'], 1)
]

texinfo_documents = [
    ('index', 'Tryme', u'Tryme Documentation',
     u'Bryan W. Berry', 'Tryme', tryme.__doc__,
     'Miscellaneous'),
]
