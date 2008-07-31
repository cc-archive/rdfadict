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
import RDF

from rdfadict.sink import DictTripleSink

class SubjectResolutionError(AttributeError):
    """Exception notifying caller that the subject can not be resolved for the
    specified node."""

class RdfaParser(object):

    HTML_RESERVED_WORDS = ('license',)
    XHTML_VOCAB_NS = "http://www.w3.org/1999/xhtml/vocab#"
    XHTML_REL_VALUES = ('alternate', 'appendix',
                        'bookmark', 'cite', 'chapter', 'contents',
                        'copyright', 'first', 'glossary', 'help', 'icon',
                        'index', 'last', 'license', 'meta', 'next', 
                        'p3pv1', 'prev', 'role', 'section', 'stylesheet',
                        'subsection', 'start', 'top', 'up')
    def __init__(self):

        self.reset()
        
    def reset(self):
        """Reset the parser, forgetting about b-nodes, etc."""

        self.__B_NODES = {}
        self.__BASE_URI = None

        # we default the cc: namespace to Creative Commons
        self.__nsmap = {'cc':'http://creativecommons.org/ns#'}
        
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

        # see if there's an explicit base set in the document;
        # if so, it overrides the URL specified as the base
        if lxml_doc.xpath('//head/base'):
            base_uri = lxml_doc.xpath('//head/base')[-1].attrib['href']

        # set the base uri for the parser
        self.__BASE_URI = base_uri

        # call the primary parser
        return self.__parse(lxml_doc, sink)

    def parseurl(self, url, sink=None):
        """Retrieve a URL and parse RDFa contained within it."""

        return self.parsestring(urllib.urlopen(url).read(), url, sink)

    def __resolve_subject(self, node):
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
                explicit_parent = None

            if explicit_parent is not None:
                return self.__resolve_safeCurie(
                    explicit_parent.attrib['about'], node)
            else:
                return None
            
        # traverse up tree looking for an about tag
        about_nodes = node.xpath('ancestor-or-self::*[@about or @resource]')
        for a_node in about_nodes[::-1]:
            if a_node == node and 'about' not in a_node.attrib:
                # only look @ about
                continue

            value = a_node.attrib.get('about', a_node.attrib.get('resource'))
            return self.__resolve_safeCurie(value, a_node)
        
        # if we get this far, we can't figure shit out
        return None

    def __resolve_uri(self, uri):
        """Resolve a (possibly) relative URI to an absolute URI.  Handle
        special cases of HTML reserved words, such as "license".

        Returns and RDF.Uri."""

        return RDF.Uri(urlparse.urljoin(self.__BASE_URI, uri))

    def __resolve_safeCurie(self, safe_curie, context):

        if not safe_curie: return None

        if safe_curie[0] == '[' and safe_curie[-1] == ']':
            return self.__resolve_curie(safe_curie[1:-1], context)
        else:
            # XXX
            return self.__resolve_uri(safe_curie)

    def __bnode(self, name):
        """Return a Blank Node."""

        return RDF.Node(blank = "%s#%s" % (self.__BASE_URI, name))

    def __resolve_curie(self, curie, context=None):

        # resolve it using our namespace map
        ns, path = curie.split(':', 1)
        if ns == '':
            ns = None

        # see if this is a blank node
        if ns == '_':
            # blank node; return an appropriate RDF.Node
            return self.__bnode(path)

        # use the namespace map of the local context if available
        if context is not None:
            ns = context.nsmap.get(ns, self.__nsmap.get(ns, None))

        else:
            # use the document namespace map
            ns = self.__nsmap.get(ns, None)

        # if we were unable to resolve the namespace, return None
        if ns is None:
            # make sure this isn't "cc:license"
            if curie.lower().strip() == 'cc:license':
                return self.__resolve_relrev('license')

            return None
            
        if ns[-1] not in ("#", "/"):
            ns = "%s#" % ns

        return RDF.Uri("%s%s" % (ns, path))

    def __resolve_relrev(self, curie_or_uri, context=None):
        """Convert a compact URI (i.e., "cc:license") to a fully-qualified
        URI.  [context] is an Element or None.  If it is not None, it will
        be used to resolve local namespace declarations.  If it is None,
        only the namespaces declared as part of the root element will be
        available.
        """
        
        """
        # is this already a uri?
        url_pieces = urlparse.urlparse(curie_or_uri)
        if '' not in [url_pieces[0], url_pieces[1]]:

            # already a valid URI
            return curie_or_uri

        # is this a urn?
        if (len(curie_or_uri) >= 4) and curie_or_uri.lower()[:4] == "urn:":
            return curie_or_uri
        """

        # determine if this CURIE has a namespace
        if ":" not in curie_or_uri:
            # no namespace; if this isn't a reserved word, we throw it away
            if curie_or_uri.lower() in self.XHTML_REL_VALUES:
                return "%s%s" % (self.XHTML_VOCAB_NS, curie_or_uri.lower())
            else:
                # not the XHTML vocabulary; no namespace, so no triple
                return None
        else:
            return self.__resolve_curie(curie_or_uri, context)

    def __get_node_contents(self, node, strip=False):
        
        if strip:
            return ""
        else:
            text = node.text or ""
            tail = node.tail or ""
            return text + "".join(
                [lxml.etree.tostring(e) for e in node]) 

    def __get_content(self, node):
        """Return the content of the node; content is returned as an
        RDF.Node with appropriate language and datatype settings."""

        # determine the actual value
        content = node.attrib.get('content', self.__get_node_contents(node))

        # look for language
        lang_nodes = node.xpath('ancestor-or-self::*[@xml:lang]')
        if lang_nodes:
            lang = lang_nodes[-1].attrib[
                '{http://www.w3.org/XML/1998/namespace}lang']
        else:
            lang = ''
        
        # look for datatype
        datatype = node.attrib.get('datatype', None)
        if datatype:
            datatype = RDF.Uri(self.__resolve_curie(datatype, node))

            # check for xsd:string
            if str(datatype) == 'http://www.w3.org/2001/XMLSchema#string':
                # fix up the literal content
                pass
                
            return RDF.Node(literal=content, language=lang, 
                            datatype=datatype)
        else:
            # no datatype
            return RDF.Node(literal=content, language=lang)

    def __parse(self, lxml_doc, sink):

        RDFA_ATTRS = ("about", "property", "rel", "rev", "href", "content")
        PRED_ATTRS = ("rel", "rev", "property")

        # extract any namespace declarations
        self.__nsmap.update(lxml_doc.nsmap)
        
        # extract triples
        # ---------------

        # using the property
        for node in lxml_doc.xpath('//*[@property]'):

            subject = self.__resolve_subject(node) or \
                RDF.Uri(self.__BASE_URI)
            obj = self.__get_content(node)

            for p in node.attrib.get('property').split():
                pred = self.__resolve_relrev(p, node)
                if pred is not None:
                    # the CURIE resolved
                    sink.triple( subject, pred, obj )
                else:
                    print obj

        # using rel
        for node in lxml_doc.xpath('//*[@rel]'):

            subj_err = None
            try:
                subject = self.__resolve_subject(node) or \
                    RDF.Uri(self.__BASE_URI)
            except SubjectResolutionError, e:
                # unable to resolve the subject; if none of the predicates
                # are namespaced, this doesn't matter... so save it for later
                subj_err = e

            # look for resource, then href to complete the triple
            obj = None
            if 'resource' in node.attrib:
                obj = self.__resolve_safeCurie(node.attrib.get('resource'),
                                               node)
            elif 'href' in node.attrib:
                obj = self.__resolve_uri(node.attrib.get('href'))
            else:
                # neither resource or href; nothing to do here
                continue

            for p in node.attrib.get('rel').split():
                pred = self.__resolve_relrev(p, node)
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
                obj = self.__resolve_subject(node) or \
                    RDF.Uri(self.__BASE_URI)
            except SubjectResolutionError, e:
                # unable to resolve the object; if none of the predicates
                # are namespaced, this doesn't matter... so save it for later
                obj_err = e

            # look for resource, then href to complete the triple
            subject = None
            if 'resource' in node.attrib:
                subject = self.__resolve_safeCurie(node.attrib.get('resource'),
                                                   node)
            elif 'href' in node.attrib:
                subject = self.__resolve_uri(node.attrib.get('href'))
            else:
                # neither resource or href; nothing to do here
                continue

            for p in node.attrib.get('rev').split():
                pred = self.__resolve_relrev(p, node)
                if pred is not None:
                    # the CURIE resolved -- 
                    # make sure we were able to resolve the subject
                    if obj_err is not None:
                        raise obj_err

                    sink.triple( subject, pred, obj )

        return sink
