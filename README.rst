========
rdfadict
========

----

🛑 **As of 2023-09-27, this project was deprecated by the new CC Legal Tools**
(cc-legal-tools-app_, cc-legal-tools-data_).

.. _cc-legal-tools-app: https://github.com/creativecommons/cc-legal-tools-app
.. _cc-legal-tools-data: https://github.com/creativecommons/cc-legal-tools-data

----


:Date: $LastChangedDate$
:Version: $LastChangedRevision$
:Author: Nathan R. Yergler <nathan@creativecommons.org>
:Organization: `Creative Commons <http://creativecommons.org>`_
:Copyright: 
   2006-2008, Nathan R. Yergler, Creative Commons; 
   licensed to the public under the `MIT license 
   <http://opensource.org/licenses/mit-license.php>`_.

An RDFa parser wth a simple dictionary-like interface.

.. contents::

Installation
************

rdfadict and its dependencies may be installed using `easy_install 
<http://peak.telecommunity.com/DevCenter/EasyInstall>`_ (recommended) ::

  $ easy_install rdfadict

or by using the standard distutils setup.py::

  $ python setup.py install

If you are installing from source, you will also need the following
packages:

* `rdflib 2.4.x <http://rdflib.net/>`_
* `pyRdfa <http://www.w3.org/2007/08/pyRdfa/>`_
* `html5lib <http://code.google.com/p/html5lib/>`_ (required if you
  want to support non-XHTML documents)

``easy_install`` will satisfy depedencies for you if necessary.
