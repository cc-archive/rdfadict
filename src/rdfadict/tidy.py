"""Simple wrapper around the tidy utility."""

import os
import sys
import string
import tempfile

from lxml.etree import ElementTree

def tidy(file):
    """Use ``tidy`` to correct inbalanced HTML.  Based on 
    elementtree.TidyTools"""


    command = ["tidy", "-q", "-asxhtml"]

    # convert
    os.system(
        "%s %s >%s.out 2>%s.err" % (string.join(command), file, file, file)
        )
    # check that the result is valid XML
    try:
        tree = ElementTree()
        tree.parse(file + ".out")
    except:
        print "*** %s:%s" % sys.exc_info()[:2]
        print ("*** %s is not valid XML "
               "(check %s.err for info)" % (file, file))
        tree = None
    else:
        if os.path.isfile(file + ".out"):
            os.remove(file + ".out")
        if os.path.isfile(file + ".err"):
            os.remove(file + ".err")

    return tree

def tidystring(in_string):
    """Use ``tidy`` to correct inbalananced HTML in the string.  Retruns an
    elementtree.

    **THIS IS NOT A THREAD SAFE CALL**
    """

    # determine the path for our temporary file
    tmp_fn = os.path.join(tempfile.gettempdir(), str(hash(in_string)))

    # write the string to the temp file for processing
    file(tmp_fn, 'w').write(in_string)

    # delegate actual tidyness to Tidy
    result = tidy(tmp_fn)

    # remove the temporary file
    os.remove(tmp_fn)

    return result

