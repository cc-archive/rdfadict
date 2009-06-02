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
import xml.dom.minidom

#import rdfadict.pyrdfa as pyrdfa
import pyRdfa
import html5lib
from html5lib import treebuilders

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

    def _make_dom(self, input_string):
        """Given an input_string containing [X]HTML, return a tuple of
        (dom, options).  If input_string is valid XML, xml.dom.minidom is 
        used to perform the parsing.  If input_string is not valid XML,
        fall back to using html5lib for creating the DOM.

        input_string is wrapped in StringIO so we can easily reset in the
        event of errors."""

        options = pyRdfa.Options()

        try:
            # try to parse as XML
            dom = xml.dom.minidom.parse(StringIO(input_string))

        except:
            # fall back to html5lib
            parser = html5lib.HTMLParser(
                tree=treebuilders.getTreeBuilder("dom"))

            dom = parser.parse(input_string, encoding='utf-8')

            # The host language has changed
            options.host_language = pyRdfa.HTML5_RDFA

        return dom, options
        
    def parse_string(self, in_string, base_uri, sink=None):

        # extract the RDFa using pyRdfa
        dom, options = self._make_dom(in_string)
        graph = pyRdfa.parseRDFa(dom, base_uri, options=options)

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

        url_contents = urllib2.urlopen(url)
        return self.parse_string(url_contents, url, sink)

    parseurl = parse_url

    def parse_file(self, file_obj, base_url, sink=None):
        """Retrieve the contents of a file-like object and parse the 
        RDFa contained within it."""

        file_contents = file_obj.read()
        return self.parse_string(file_contents, base_url, sink)

        return sink
