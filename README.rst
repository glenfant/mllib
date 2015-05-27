=====
mllib
=====

A REST client for MarkLogic 8

MarkLogic 8 is a NOSQL database and application framework for documentation management applications.

Developer notes
===============

Please use a virtualenv to maintain this package, but I should not need to say that.

Grab the source from the SCM repository
---------------------------------------

.. code:: console

  $ python setup.py develop
  $ pip install mllib[dev]

Run the tests
-------------

Running the tests require :

- Connection to http://httpbin.org/ . If you can see its home page in your browser, it's OK

- Running a MarkLogic 8 REST tests instance at http://localhost:8000 with
  username and password being both ``admin``. If you prefer to use another
  instance listening on port ``9000`` of host ``my.marklogic-rest.tld`` and
  which user is ``foo`` authenticated by password ``bar``, you need to provide
  this in a ``MLLIB_TEST_SERVER`` environment variable that contains
  ``my.marklogic-rest.tld:9000:foo:bar``.

  if your MarkLogic REST server expects an HTTP Basic Authentication token, append
  ``:basic`` to the ``MLLIB_TEST_SERVER`` environment variable. Otherwise an HTTP
  Digest Auth token will be issued.

.. code:: console

  $ export MLLIB_TEST_SERVER=my.marklogic-rest.tld:9000:foo:bar  # Optional
  $ python setup.py test
  $ python run_tests.py

.. rubric:: Build the Sphinx documentation:

.. code:: console

   $ python setup.py build_sphinx
   $ firefox build/sphinx/html/index.html


Links
=====

FIXME: Provide real links

Project home page

  http://www.mystuff.com/project

Source code

  http://www.mystuff.com/source

Issues tracker

  http://www.mystuff.com/issues

Credits
=======

The development of this library is sponsored by the `Assemblée Nationale
<http://www.assemblee-nationale.fr/>`_ (France's Chamber of Deputies).

License
=======

This software is distributed under the terms of the `MIT license
<http://opensource.org/licenses/MIT>`_.
