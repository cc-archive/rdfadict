
Usage
*****

.. admonition:: Document Purpose

     This document is intended to provide a set of literate tests
     for the ``rdfadict`` package; it is **not** intended to provide thorough
     coverage of RDFa syntax or semantics.  See the `RDF Primer 
     <http://www.w3.org/2006/07/SWD/RDFa/primer/>`_ or the `RDFa Syntax 
     <http://www.w3.org/2006/07/SWD/RDFa/syntax/>`_ for details on RDFa.

**rdfadict** parses RDFa metadata encoded in HTML or XHTML documents.  It can
parse a block of text (as a string), or a URL.  For example, given the 
following block of sample text:

  >>> rdfa_sample = """
  ... <div xmlns:dc="http://purl.org/dc/elements/1.1/"
  ...      xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  ... <h1 property="dc:title">Vacation in the South of France</h1>
  ... <h2>created 
  ... by <span property="dc:creator">Mark Birbeck</span>
  ... on <span property="dc:date" type="xsd:date"
  ...          content="2006-01-02">
  ...   January 2nd, 2006
  ...    </span>
  ... </h2>
  ... </div>"""

Triples can be extracted using **rdfadict**:

  >>> import rdfadict
  >>> base_uri = "http://example.com/rdfadict/"
  >>> parser = rdfadict.RdfaParser()
  >>> triples = parser.parse_string(rdfa_sample, base_uri)

We define the variable ``base_uri`` to let the parser know what URI assertions
without subjects apply to.  

Based on our example text, we expect to get three triples back -- title, 
creator and date.  Triple are indexed as a dictionary, first by subject,
then by predicate, finally retuning a ``list`` of objects.  For example, 
a list of all subjects is retrieved using:

  >>> triples.keys()
  ['http://example.com/rdfadict/']

If assertions were made about resources other than the default, those URIs
would appear in this list.  We can verify how many predicates were found
for this subject by accessing the next level of the dictionary:

  >>> len(triples['http://example.com/rdfadict/'].keys())
  3

Finally, we can retrieve the value for the title by fully dereferencing
the dictionary:

  >>> triples['http://example.com/rdfadict/'][
  ...     'http://purl.org/dc/elements/1.1/title']
  ['Vacation in the South of France']

Note that the objects are stored as a list by the default triple sink.

Multiple Assertions
===================

Because the ``property`` attribute always denotes triple with a literal string
as its object and ``rel`` and ``rev`` denote triples with URIs as their 
objects, it is possible to make multiple assertions with a single HTML tag.

For example:

  >>> multi_rdfa = """
  ... <div xmlns:foaf="http://xmlns.com/foaf/0.1/" 
  ...      xmlns:dc="http://purl.org/dc/elements/1.1/">
  ...   This photo was taken by <a about="photo1.jpg" property="dc:title"
  ...   content="Portrait of Mark" rel="dc:creator"
  ...   rev="foaf:img" 
  ...   href="http://www.blogger.com/profile/1109404">Mark Birbeck</a>.
  ... </div>
  ... """

In this statement we are making three assertions: two involving URI objects
(specified by ``rel`` and ``rev``), and one involving the ``property``.

  >>> import rdfadict
  >>> parser = rdfadict.RdfaParser()
  >>> multi_base_uri = "http://example.com/multiassert/"
  >>> triples = parser.parse_string(multi_rdfa, multi_base_uri)

We expect the triples generated to have two subjects: the photo URI (for the 
``rel`` and ``property`` assertions) and the ``href`` URI (for the ``rev``
assertion).

  >>> len(triples.keys()) == 2
  True
  >>> 'http://example.com/multiassert/photo1.jpg' in triples.keys()
  True
  >>> 'http://www.blogger.com/profile/1109404' in triples.keys()
  True

Finally, we verify that the assertions made about each subject are correct:

  >>> len(triples['http://example.com/multiassert/photo1.jpg'].keys()) == 2
  True
  >>> triples['http://example.com/multiassert/photo1.jpg'] \
  ...          ['http://purl.org/dc/elements/1.1/creator']
  ['http://www.blogger.com/profile/1109404']
  >>> triples['http://example.com/multiassert/photo1.jpg'] \
  ...          ['http://purl.org/dc/elements/1.1/title']
  ['Portrait of Mark']

  >>> triples['http://www.blogger.com/profile/1109404']
  {'http://xmlns.com/foaf/0.1/img': ['http://example.com/multiassert/photo1.jpg']}


Resolving Statements
====================

When resolving statements, the REL, REV, CLASS and PROPERTY attributes expect
a `CURIE <http://www.w3.org/2001/sw/BestPractices/HTML/2005-10-21-curie>`_, 
while the HREF property expects a URI.  When resolving CURIEs, un-namespaced 
values which are not HTML reserved words (such as license) are ignored to 
prevent "triple bloat".

Given an example:

  >>> rdfa_sample2 = """
  ... <div xmlns:dc="http://purl.org/dc/elements/1.1/"
  ...      xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  ... <link rel="alternate" href="/foo/bar" />
  ... <h1 property="dc:title">Vacation in the South of France</h1>
  ... <h2>created 
  ... by <span property="dc:creator">Mark Birbeck</span>
  ... on <span property="dc:date" type="xsd:date"
  ...          content="2006-01-02">
  ...   January 2nd, 2006
  ...    </span>
  ... </h2>
  ... <img src="/myphoto.jpg" class="photo" />
  ... (<a href="http://creativecommons.org/licenses/by/3.0/" rel="license"
  ...    about="/myphoto.jpg">CC License</a>)
  ... </div>"""

We can extract RDFa triples from it:

  >>> parser = rdfadict.RdfaParser()
  >>> base_uri2 = "http://example.com/rdfadict/sample2"
  >>> triples = parser.parse_string(rdfa_sample2, base_uri2)

This block of RDFa includes a license statement about another document, the
photo:

  >>> len(triples["http://example.com/myphoto.jpg"])
  1

  >>> triples["http://example.com/myphoto.jpg"].keys()
  ['http://www.w3.org/1999/xhtml/vocab#license']
  >>> triples["http://example.com/myphoto.jpg"] \
  ...    ['http://www.w3.org/1999/xhtml/vocab#license']
  ['http://creativecommons.org/licenses/by/3.0/']

There are two things to note with respect to this example.  First, the relative
URI for the photo is resolved with respect to the ``base_uri`` value.  Second,
the "class" attribute is not processed, because it's value is not in a 
declared namespace:

  >>> 'photo' in [ n.lower() for n in
  ...      triples['http://example.com/rdfadict/sample2'].keys() ]
  False

Similar to this case is the ``link`` tag in the example HTML.  Based on the
subject resolution rules for ``link`` and ``meta`` tags, no subject can be 
resolved for this assertion.  However, this does not throw an exception because
the value of the ``rel`` attribute is not namespaced.

Consider an alternative, contrived example:

  >>> link_sample = """
  ... <div xmlns:dc="http://purl.org/dc/elements/1.1/"
  ...      xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...      about="http://example.com/">
  ... <link rel="dc:creator" href="http://example.com/birbeck" />
  ... </div>"""

Based on the subject resolution rules for ``link`` tags, we expect to see
one assertion: that http://example.com/birbeck represents the creator of
http://example.com.  This can be tested; note we supply a different 
``base_uri`` to ensure the subject is being properly resolved.

  >>> parser = rdfadict.RdfaParser()
  >>> link_base_uri = 'http://example.com/foo'
  >>> triples = parser.parse_string(link_sample, link_base_uri)

  >>> triples.keys()
  ['http://example.com/']
  >>> len(triples['http://example.com/'])
  1
  >>> triples['http://example.com/']['http://purl.org/dc/elements/1.1/creator']
  ['http://example.com/birbeck']

Note that this HTML makes **no** assertions about the source document:

  >>> link_base_uri in triples.keys()
  False

If the HTML sample is modified slightly, and the ``about`` attribute
is omitted, rdfadict is resolves the subject to the explicit base URI.

  >>> link_sample = """
  ... <div xmlns:dc="http://purl.org/dc/elements/1.1/"
  ...      xmlns:xsd="http://www.w3.org/2001/XMLSchema" >
  ... <link rel="dc:creator" href="http://example.com/birbeck" />
  ... </div>"""
  >>> parser = rdfadict.RdfaParser()
  >>> link_base_uri = 'http://example.com/foo'
  >>> triples = parser.parse_string(link_sample, link_base_uri)
  >>> link_base_uri in triples.keys()
  True

If a namespace is unable to be resolved, the assertion is ignored.

  >>> ns_sample = """
  ... <a href="http://example.com/foo" rel="foo:bar">Content</a>
  ... """
  >>> parser = rdfadict.RdfaParser()
  >>> triples = parser.parse_string(ns_sample, 'http://example.com/bob')
  >>> triples
  {}

See the `RDFa Primer <http://www.w3.org/2006/07/SWD/RDFa/primer/>`_
for more RDFa examples.

Parsing Files
=============

**rdfadict** can parse from three sources: URLs, file-like objects, or
strings.  The examples thus far have parsed strings using the
``parse_string`` method.  A file-like object can also be used:

   >>> from StringIO import StringIO
   >>> file_sample = """
   ... <html>
   ...  <body>
   ...    <a href="http://creativecommons.org/licenses/by/3.0/"
   ...       rel="license">the license</a>
   ...  </body>
   ... </html>
   ... """
   >>> parser = rdfadict.RdfaParser()
   >>> result = parser.parse_file(StringIO(file_sample),
   ...                            "http://creativecommons.org")
   >>> result.keys()
   ['http://creativecommons.org']
   >>> result['http://creativecommons.org']
   {'http://www.w3.org/1999/xhtml/vocab#license': ['http://creativecommons.org/licenses/by/3.0/']}

Parsing By URL
==============

**rdfadict** can parse a document retrievable by URI.  Behind the
scenes it uses ``urllib2`` to open the document.  

  >>> parser = rdfadict.RdfaParser()
  >>> result = \
  ... parser.parse_url('http://creativecommons.org/licenses/by/2.1/jp/')
  >>> print result['http://creativecommons.org/licenses/by/2.1/jp/']\
  ... ['http://purl.org/dc/elements/1.1/title'][0]
  表示 2.1 日本

Note that ``parse_file`` is not recommended for use with ``urllib2``
handler objects.  In the event that pyRdfa encounters a non-XHTML
source, it re-opens the URL to begin processing with a more tolerant
parser.  When ``parse_file`` is used to initiate parsing, it is unable
to re-open the URL correctly.

Triple Sinks
============

**rdfadict** uses a simple interface (the triple sink) to pass RDF triples
extracted back to some storage mechanism.  A class which acts as a triple
sink only needs to define a single method, ``triple``.  For example::

   class StdOutTripleSink(object):
       """A triple sink which prints out the triples as they are received."""

       def triple(self, subject, predicate, object):
           """Process the given triple."""

           print subject, predicate, object

The default triple sink models the triples as a nested dictionary, 
as described above.  Also included with the package is a list triple sink,
which stores the triples as a list of 3-tuples.  To use a different sink,
pass an instance in as the ``sink`` parameter to either parse method.  For
example:

   >>> parser = rdfadict.RdfaParser()
   >>> list_sink = rdfadict.sink.SimpleTripleSink()
   >>> result = parser.parse_string(rdfa_sample, base_uri, sink=list_sink)

   >>> result is list_sink
   True

   >>> len(list_sink)
   3

Note that the parse method returns the sink used.  Since the sink we're using
is really just a ``list``, the interpreter prints the contents upon return.

Limitations and Known Issues
****************************

**rdfadict** currently does not implement the following areas properly; 
numbers in parenthesis refer to the section number  in the `RDFa Syntax 
Document <http://www.w3.org/2006/07/SWD/RDFa/syntax/>`_.

* ``xml:base`` is not respected (2.3)
* Typing is not implemented; this includes implicit XMLLiteral typing as well
  as explicit types specified by the ``datatype`` attribute (5.1)
* Blank nodes are not guaranteed to work per the syntax document (5.2); if
  you try to use them, you will probably be disappointed.
* Reification is not implemented (5.3).

