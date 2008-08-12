## Copyright (c) 2006-2008 Nathan R. Yergler, Creative Commons

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

"""Triple sinks which support adding to RDF graphs."""

class GraphSink(object):
    """A triple sink which adds new triples to an existing rdflib graph."""

    def __init__(self, graph):
        self.graph = graph

    def triple(self, s, p, o):

        # XXX dereference the URIs, literals to plain strings
        self.graph.add( (s,p,o) )

class RedlandModelSink(object):
    """A sink which wraps a Redland Model."""

    def __init__(self, model):
        self.model = model

    def triple(self, s, p, o):

        import RDF

        self.model.append(RDF.Statement(s, p, o))


"""
class RdfStoreSink(ccrdf.rdfdict.rdfStore):

    def __init__(self):
        super(RdfStoreSink, self).__init__()

    def triple(self, s, p, o):

        self.store.add( (s,p,o) )

"""
