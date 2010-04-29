## Copyright (c) 2006-2007 Nathan R. Yergler, Creative Commons

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

"""Simple triple Sink objects."""

import sys

if sys.version < (2,5):
    # import set support
    from sets import Set as set

class SimpleTripleSink(list):
    """A bare-bones Triple sink that just stores them as a list of tuples."""

    def triple(self, s, p, o):

        self.append( (str(s),str(p),str(o)) )

class DictTripleSink(dict):

    def triple(self, s, p, o):
        """Add a triple [s, p, o] to the triple dictionary."""

        self.setdefault(s.encode('utf-8'), {}).setdefault(p.encode('utf-8'), [])
        self[s.encode('utf-8')][p.encode('utf-8')].append(o.encode('utf-8'))

class DictSetTripleSink(dict):

    def triple(self, s, p, o):
        """Add a triple [s, p, o] to the triple dictionary."""

        self.setdefault(unicode(s), {}).setdefault(unicode(p), set())
        self[unicode(s)][unicode(p)].add(unicode(o))
