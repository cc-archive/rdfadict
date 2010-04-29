## Copyright (c) 2006-2009 Nathan R. Yergler, Creative Commons

## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the "Software"),
## to deal in the Software without restriction, including without limitation
## the rights to use, copy, modify, merge, publish, distribute, sublicense,
## and/or sell copies of the Software, and to permit persons to whom the
## Software is furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
## DEALINGS IN THE SOFTWARE.

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = "rdfadict",
    version = "0.7.2",
    packages = ['rdfadict', 'rdfadict.sink', 'rdfadict.tests',],
    package_dir = {'':'src'},

    entry_points = {
        'ccrdf.extract_to_graph': [
            'rdfa = rdfadict:extract [ccrdf]',
            ],
        
        'console_scripts' : [
            'tf_test = rdfadict.tests.test_taskforce:cli',
            ]
        },
    
    install_requires = ['setuptools',
                        'rdflib',
                        'html5lib',
                        'pyRdfa>=2.3.4',
                        ],
    dependency_links = [
        'http://dev.w3.org/2004/PythonLib-IH/dist/pyRdfa-2.3.4.tar.gz',
        ],

    include_package_data = True,
    zip_safe = True,

    author = 'Nathan R. Yergler',
    author_email = 'nathan@creativecommons.org',
    description = 'An RDFa parser wth a simple dictionary-like interface.',
    long_description=(
         read('README')
         + '\n' +
         read('src', 'rdfadict', 'README.txt')
         + '\n' + 
         read('CHANGES')
         + '\n' +
         'Download\n'
         '********\n'
         ),
    license = 'MIT',
    url = 'http://wiki.creativecommons.org/RdfaDict',

    )
