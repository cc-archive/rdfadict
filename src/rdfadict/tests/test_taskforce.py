"""Test harness for running the Task Force RDFa tests against rdfadict."""

import sys
import new
import unittest
import urllib2
import string
import logging

from rdflib import ConjunctiveGraph as Graph
from rdflib.sparql.parser import doSPARQL

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

MANIFESTS =[ 
    "http://www.w3.org/2006/07/SWD/RDFa/testsuite/xhtml1-testcases/rdfa-xhtml1-test-manifest.rdf",
    ]

APPROVED_TESTS = """
PREFIX test: <http://www.w3.org/2006/03/test-description#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>

SELECT ?testcase ?title ?description ?source ?result WHERE {
   ?testcase rdf:type test:TestCase .
   ?testcase test:reviewStatus test:approved .
   ?testcase dc:title ?title .
   ?testcase test:purpose ?description .
   ?testcase test:informationResourceInput ?source .
   ?testcase test:informationResourceResults ?result .
}
"""

def py_name(input):
    """Take a string and return a valid Python identifier."""

    input = input.replace(' ', '_')
    return "".join([c for c in input if c in 
                    string.ascii_letters + '_' + string.digits])

class TaskForceTest(unittest.TestCase):

    def __init__(self, testcase, title, description, source, result):
        super(TaskForceTest, self).__init__()

        self._uri = str(testcase)
        self._name = str(title)
        self._description = str(description)

        self._source = str(source)
        self._result = urllib2.urlopen(str(result)).read()

    def id(self):
        return self._name

    def shortDescription(self):
        return "%s: %s (%s)" % (self._name, self._description, self._uri)

    def runTest(self):
        """Run the specified task force test."""
        import rdfadict
        import rdfadict.sink.graph

        print self._uri

        # set up our target sink
        g = Graph()
        sink = rdfadict.sink.graph.GraphSink(g)

        # run rdfadict over the input
        parser = rdfadict.RdfaParser()
        parser.parseurl(self._source, sink)
        
        # execute the test SPARQL
        g.query(self._result)

        print g.selected
        # self.assert_(test.execute(g).get_boolean())

def test_suite():
    """Generate a test suite of all approved task force tests."""

    test_suite = unittest.TestSuite()

    return test_suite

    for manifest in MANIFESTS:

        LOG.debug("Retrieving manifest %s" % manifest)

        test_manifest = Graph()
        test_manifest.parse(manifest)

        # find all the approved tests'
        for result in test_manifest.query(APPROVED_TESTS):
            LOG.debug("Adding test case: %s" % str(result[3]))

            test_suite.addTest(
                new.classobj(py_name(str(result[3])),
                             (TaskForceTest,),{})(*result))

    return test_suite

def get_test(uri):
    """Return a single test case for the specified URI."""

    for manifest in MANIFESTS:

        LOG.debug("Retrieving manifest %s" % manifest)

        test_manifest = Graph()
        test_manifest.parse(manifest)

        # find all the approved tests'
        for result in test_manifest.query(APPROVED_TESTS):

            if str(result[0]) == uri:
                return new.classobj(py_name(str(result[3])),
                                    (TaskForceTest,),{})(*result)

    return None

def cli():
    """Command line interface for retrieving and running a Task Force 
    tests.  If run without command line parameters, runs all available
    tests; if run with a single URI, attempts to retrieve that test from
    known manifests."""

    if len(sys.argv) > 1: 
        # running a single test 
        test_uri = sys.argv[-1] 
        test = get_test(test_uri)

        LOG.debug("Retrieved test %s" % test_uri) 
    else: 
        test = test_suite()

    unittest.TextTestRunner().run(test)

    LOG.info("Done.")

if __name__ == '__main__':
    all()
