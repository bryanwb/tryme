# -*- coding: utf-8 -*-
import sys
from os import path
from distutils.core import setup


VERSION = '0.0.1'

if sys.version_info < (2, 7):
    sys.exit('tryme requires Python 2.7 or higher')

ROOT_DIR = path.abspath(path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

LONG_DESCRIPTION = open(path.join(ROOT_DIR, 'README.rst')).read()

setup(
    name='tryme',
    version=VERSION,
    description='Error handling for humans',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    author='Bryan W. Berry',
    author_email='bryan.berry@gmail.com',
    url='https://github.com/bryanwb/tryme/',
    download_url=(
        'https://github.com/bryanwb/tryme/archive/%s.zip' % VERSION),
    packages=['tryme'],
    license='BSD-New',
)
