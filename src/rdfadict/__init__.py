## Copyright (c) 2006 Nathan R. Yergler, Creative Commons

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

import urllib
import urlparse

import lxml.etree

class SimpleTripleSink(list):
    """A bare-bones Triple sink that just stores them as a list of tuples."""

    def triple(self, s, p, o):

        self.append( (s,p,o) )

class DictTripleSink(dict):

    def triple(self, s, p, o):
        """Add a triple [s, p, o] to the triple dictionary."""

        self.setdefault(s, {}).setdefault(p, [])
        self[s][p].append(o)

class RdfaParser(object):

    def __init__(self):

        self.reset()

    def reset(self):
        """Reset the parser, forgetting about b-nodes, etc."""

        self.__bnodes = {}
        self.__nsmap = {None:'http://www.w3.org/1999/xhtml',
                        }

##                         'cc':'http://web.resource.org/cc/',
##                         'dc':'http://purl.org/dc/elements/1.1/',
##                         'ex':'http://example.org/',
##                         'foaf':'http://xmlns.com/foaf/0.1/',
##                         'rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
##                         'rdfs':'http://www.w3.org/2000/01/rdf-schema#',
##                         'svg':'http://www.w3.org/2000/svg',
##                         'xh11':'http://www.w3.org/1999/xhtml',
##                         'xsd':'http://www.w3.org/2001/XMLSchema#',
##                         'biblio':'http://example.org/biblio/0.1',
##                         'taxo':'http://purl.org/rss/1.0/modules/taxonomy/',
                        
    def parsestring(self, in_string, base_uri, sink=DictTripleSink()):

        try:
            lxml_doc = lxml.etree.fromstring(in_string)
        except lxml.etree.XMLSyntaxError, e:

            # try to parse as HTML
            lxml_doc = lxml.etree.fromstring(in_string,
                                             lxml.etree.HTMLParser())

        return self.__parse(lxml_doc, base_uri, sink)

    def parseurl(self, url, sink=DictTripleSink()):
        """Retrieve a URL and parse RDFa contained within it."""

        return self.parsestring(urllib.urlopen(url).read(), url, sink)

    def __resolve_subject(self, node):

        # check for meta or link which don't traverse up the entire tree
        if node.tag in ('link', 'meta'):
            # look for an about attribute on the node or its parent
            explicit_parent = node.attrib.get('about',
                                              (node.getparent() and
                                               node.getparent().attrib.get(
                'about', False)))

            if explicit_parent:
                return self.__resolve_uri(explicit_parent)
            else:
                # no explicitly defined parent, perform reification
                # XXX Does not handle head in XHTML2 docs; see 4.3.3.1 in spec
                raise NotImplementedError("reification not supported.")
                
        # traverse up tree looking for an about tag
        about_nodes = node.xpath('ancestor-or-self::*/@about')
        if about_nodes:
            return self.__resolve_uri(about_nodes[-1])
        else:
            return None

    def __resolve_uri(self, curie_or_uri):

        # is this already a uri?
        url_pieces = urlparse.urlparse(curie_or_uri)
        if '' not in [url_pieces[0], url_pieces[1]]:

            # already a valid URI
            return curie_or_uri

        # resolve it using our namespace map
        if ":" not in curie_or_uri:
            curie_or_uri = ":%s" % curie_or_uri

        ns, path = curie_or_uri.split(':', 1)
        if ns == '':
            ns = None

        ns = self.__nsmap[ns]

        if ns[-1] not in ("#", "/"):
            ns = "%s#" % ns

        return "%s%s" % (ns, path)
    
    def __parse(self, lxml_doc, base_uri='', sink=DictTripleSink()):

        RDFA_ATTRS = ("about", "property", "rel", "rev", "href", "content")
        PRED_ATTRS = ("rel", "rev", "property")

        # extract any namespace declarations
        self.__nsmap.update(lxml_doc.nsmap)
        
        # extract triples
        # ---------------

        # using the property
        for node in lxml_doc.xpath('//*[@property]'):

            subject = self.__resolve_subject(node) or base_uri
            obj = node.attrib.get('content', node.text)

            for p in node.attrib.get('property').split():
                sink.triple( subject, self.__resolve_uri(p), obj )

        # using rel
        for node in lxml_doc.xpath('//*[@rel]'):

            subject = self.__resolve_subject(node) or base_uri
            obj = self.__resolve_uri(node.attrib.get('href'))

            for p in node.attrib.get('rel').split():
                sink.triple( subject, self.__resolve_uri(p), obj )

        # using rev
        for node in lxml_doc.xpath('//*[@rev]'):

            obj = self.__resolve_subject(node) or base_uri
            subject = self.__resolve_uri(node.attrib.get('href'))

            for p in note.attrib.get('rel').split():
                sink.triple( subject, self.__resolve_uri(p), obj )

        return sink
    
if __name__ == '__main__':

    import pprint
    
    parser = RdfaParser()
    triples = parser.parseurl("http://rdfa.info")
    print triples
    
    
