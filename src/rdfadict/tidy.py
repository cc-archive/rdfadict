"""Simple wrapper around the tidy utility."""

import tidy
import lxml.etree

def tidystring(doc_str, options = None):
    """Use ``tidy`` to correct inbalananced HTML in the string.  Returns an
    elementtree.
    """

    if options is None:
        options = dict(output_xhtml=1,  
                       add_xml_decl=1,  
                       indent=1, 
                       tidy_mark=0)

    tidied_str = tidy.parseString(doc_str, **options)

    return lxml.etree.fromstring(tidied_str)

