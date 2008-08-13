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

import urllib2
import urlparse
from cStringIO import StringIO

import rdfadict.pyrdfa as pyrdfa

from rdfadict.sink import DictTripleSink

class SubjectResolutionError(AttributeError):
    """Exception notifying caller that the subject can not be resolved for the
    specified node."""

class RdfaParser(object):
        
    def reset(self):
        """Reset the parser, forgetting about b-nodes, etc."""

        # this is a no-op now that we're using pyRdfa

    def _graph_to_sink(self, graph, sink):
        """Read assertions from the rdflib Graph and pass them to the sink."""

        for s, p, o in graph:
            sink.triple(s,p,o)

        return sink

    def parse_string(self, in_string, base_uri, sink=None):

        # extract the RDFa using pyRdfa
        stream = StringIO(in_string)
        graph = pyrdfa.processFile(stream, base=base_uri)

        # see if a default sink is required
        if sink is None:
            sink = DictTripleSink()

        # transform from graph to sink
        self._graph_to_sink(graph, sink)
        del graph

        return sink
    parsestring = parse_string

    def parse_url(self, url, sink=None):
        """Retrieve a URL and parse RDFa contained within it."""

        # construct a request and open it
        opener = urllib2.build_opener()
        request = urllib2.Request(url)
        request.add_header('User-Agent',
                 'Python rdfadict/0.5.1 http://pypi.python.org/pypi/rdfadict')

        # delegate to parse_file
        return parse_file(opener.open(request), url, sink=sink)
    parseurl = parse_url

    def parse_file(self, file_obj, base_url, sink=None):
        """Retrieve the contents of a file-like onject and parse the 
        RDFa contained within it."""

        # extract the RDFa using pyRdfa
        graph = pyrdfa.processFile(file_obj, base=base_url)

        # see if a default sink is required
        if sink is None:
            sink = DictTripleSink()

        # transform from graph to sink
        self._graph_to_sink(graph, sink)
        del graph

        return sink
