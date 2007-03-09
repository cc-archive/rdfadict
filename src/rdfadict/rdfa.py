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

import urllib
import urlparse

import lxml.etree

from rdfadict.sink import DictTripleSink

class SubjectResolutionError(AttributeError):
    """Exception notifying caller that the subject can not be resolved for the
    specified node."""

class RdfaParser(object):

    HTML_RESERVED_WORDS = ('license',)

    def __init__(self):

        self.reset()
        self.__REIFY_COUNTER = 0
        
    def reset(self):
        """Reset the parser, forgetting about b-nodes, etc."""

        self.__bnodes = {}
        self.__nsmap = {}
        
##        self.__nsmap = {None:'http://www.w3.org/1999/xhtml',
##                        }
##
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
                        
    def parsestring(self, in_string, base_uri, sink=None):

        # see if a default sink is required
        if sink is None:
            sink = DictTripleSink()

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

    def __resolve_subject(self, node, base_uri):
        """Resolve the subject for a particular node, with respect to the 
        base URI.  If the subject can not be resolved, return None.

        XXX Note that this does not perform reification.  At all.
        """

        # check for meta or link which don't traverse up the entire tree
        if node.tag in ('link', 'meta'):
            # look for an about attribute on the node or its parent
            if node.attrib.get('about', False):
                explicit_parent = node
            elif node.getparent().attrib.get('about', False):
                explicit_parent = node.getparent()
            else:
                explicit_parent = False

            if explicit_parent:
                return self.__resolve_uri(explicit_parent.attrib['about'],
                                          base_uri)
            else:
                # XXX Does not handle head in XHTML2 docs; see 4.3.3.1 in spec
                # no explicitly defined parent, perform reification
                raise SubjectResolutionError(
                    "Unable to resolve subject for node.")
            
        # traverse up tree looking for an about tag
        about_nodes = node.xpath('ancestor-or-self::*[@about]')
        if about_nodes:
            return self.__resolve_uri(about_nodes[-1].attrib['about'],
                                      base_uri)
        else:
            return None

    def __resolve_uri(self, uri, base_uri):
        """Resolve a (possibly) relative URI to an absolute URI.  Handle
        special cases of HTML reserved words, such as "license"."""

        return urlparse.urljoin(base_uri, uri)

    def __resolve_curie(self, curie_or_uri, context=None):
        """Convert a compact URI (i.e., "cc:license") to a fully-qualified
        URI.  [context] is an Element or None.  If it is not None, it will
        be used to resolve local namespace declarations.  If it is None,
        only the namespaces declared as part of the root element will be
        available.
        """
        
        # is this already a uri?
        url_pieces = urlparse.urlparse(curie_or_uri)
        if '' not in [url_pieces[0], url_pieces[1]]:

            # already a valid URI
            return curie_or_uri

        # is this a urn?
        if (len(curie_or_uri) >= 4) and curie_or_uri.lower()[:4] == "urn:":
            return curie_or_uri

        # determine if this CURIE has a namespace
        if ":" not in curie_or_uri:
            # no namespace; if this isn't a reserved word, we throw it away
            if curie_or_uri.lower() not in self.HTML_RESERVED_WORDS:
                return None
            else:
                # reserved word; map it to the XHTML namespace
                return "http://www.w3.org/1999/xhtml#%s" % curie_or_uri

        # resolve it using our namespace map
        ns, path = curie_or_uri.split(':', 1)
        if ns == '':
            ns = None

        if context is not None:
            ns = context.nsmap[ns]

        else:
            ns = self.__nsmap[ns]
            
        if ns[-1] not in ("#", "/"):
            ns = "%s#" % ns

        return "%s%s" % (ns, path)
    
    def __parse(self, lxml_doc, base_uri, sink):

        RDFA_ATTRS = ("about", "property", "rel", "rev", "href", "content")
        PRED_ATTRS = ("rel", "rev", "property")

        # extract any namespace declarations
        self.__nsmap.update(lxml_doc.nsmap)
        
        # extract triples
        # ---------------

        # using the property
        for node in lxml_doc.xpath('//*[@property]'):

            subject = self.__resolve_subject(node, base_uri) or base_uri
            obj = node.attrib.get('content', node.text)

            for p in node.attrib.get('property').split():
                pred = self.__resolve_curie(p, node)
                if pred is not None:
                    # the CURIE resolved
                    sink.triple( subject, pred, obj )

        # using rel
        for node in lxml_doc.xpath('//*[@rel]'):

            subj_err = None
            try:
                subject = self.__resolve_subject(node, base_uri) or base_uri
            except SubjectResolutionError, e:
                # unable to resolve the subject; if none of the predicates
                # are namespaced, this doesn't matter... so save it for later
                subj_err = e

            obj = self.__resolve_uri(node.attrib.get('href'), base_uri)

            for p in node.attrib.get('rel').split():
                pred = self.__resolve_curie(p, node)
                if pred is not None:
                    # the CURIE resolved -- 
                    # make sure we were able to resolve the subject
                    if subj_err is not None:
                        raise subj_err

                    sink.triple( subject, pred, obj )

        # using rev
        for node in lxml_doc.xpath('//*[@rev]'):

            obj_err = None
            try:
                obj = self.__resolve_subject(node, base_uri) or base_uri
            except SubjectResolutionError, e:
                # unable to resolve the object; if none of the predicates
                # are namespaced, this doesn't matter... so save it for later
                obj_err = e

            subject = self.__resolve_uri(node.attrib.get('href'), base_uri)

            for p in node.attrib.get('rev').split():
                pred = self.__resolve_curie(p, node)
                if pred is not None:
                    # the CURIE resolved -- 
                    # make sure we were able to resolve the subject
                    if obj_err is not None:
                        raise obj_err

                    sink.triple( subject, pred, obj )

        return sink
