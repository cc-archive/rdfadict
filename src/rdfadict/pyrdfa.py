"""Wrapper around pyRdfa."""

import pyRdfa
from pyRdfa import *

def _process_DOM(dom, base, outputFormat, options, local=False) :
    """
    Modified verison of pyRdfa._process_DOM; returns the rdflib Graph
    instead of serializing the output.
    
    -- nathan@creativecommons.org 2008-08-07
    
    /////////////////////////////////////////////////////////////////


    Core processing. The transformers ("pre-processing") is done
    on the DOM tree, the state is initialized, and the "real" RDFa parsing is done. Finally,
    the result (which is an RDFLib Graph) is serialized using RDFLib's serializers.

    The real work is done in the L{parser function<Parse.parse_one_node>}.

    @param dom: XML DOM Tree node (for the top level)
    @param base: URI for the default "base" value (usually the URI of the file to be processed)
    @param outputFormat: serialization format
    @param options: Options for the distiller
    @type options: L{Options}
    @keyword local: whether the call is for a local usage or via CGI (influences the way
    exceptions are handled)
    @return: serialized graph
    @rtype: string
    """

    # Create the RDF Graph
    graph = Graph()
    # get the DOM tree

    html = dom.documentElement

    # Perform the built-in and external transformations on the HTML tree. This is,
    # in simulated form, the hGRDDL approach of Ben Adida
    for trans in options.transformers + builtInTransformers :
        trans(html,options)

    # collect the initial state. This takes care of things
    # like base, top level namespace settings, etc.
    # Ensure the proper initialization
    state = ExecutionContext(html, graph, base=base, options=options)

    # The top level subject starts with the current document; this
    # is used by the recursion
    subject = URIRef(state.base)

    # parse the whole thing recursively and fill the graph
    if local :
        parse_one_node(html, graph, subject, state,[])
        if options.warnings:
            for t in options.comment_graph.graph : graph.add(t)
        # NRY 2008-08-07 # retval = graph.serialize(format=outputFormat)
    else :
        # This is when the code is run as part of a Web CGI service. The
        # difference lies in the way exceptions are handled...
        try :
            # this is a recursive procedure through the full DOM Tree
            parse_one_node(html, graph, subject, state,[])
        except :
            # error in the input...
            (type,value,traceback) = sys.exc_info()
            msg = 'Error in RDFa content: "%s"' % value
            raise RDFaError, msg
        # serialize the graph and return the result
        # NRY 2008-08-07 # retval = None
        try :
            if options.warnings :
                for t in options.comment_graph.graph : 
                    graph.add(t)
            # NRY 2008-08-07 # retval = graph.serialize(format=outputFormat)
        except :
            # XML Parsing error in the input
            (type,value,traceback) = sys.exc_info()
            msg = 'Error in graph serialization: "%s"' % value
            raise RDFaError, msg

    # NRY 2008-08-07 # return retval
    return graph

pyRdfa._process_DOM = _process_DOM

__all__ = ['processURI', 'processFile',]
