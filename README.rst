=====
mllib
=====

A REST client for `MarkLogic 8 <http://www.marklogic.com/>`_ documentation
management.

`MarkLogic 8`_ is a NOSQL database and application framework for documentation
management applications.

This package is still at an early WIP state and APIs may change before the
first release.

As said in the subtitle, this package focuses on **documentation management
services** (CRUD operations, searching, ...). If you need a pythonic way to
create, fine tune and populate `MarkLogic 8`_ databases and clusters, you may
prefer `MarkLogic_Python <https://github.com/paul-hoehne/MarkLogic_Python>`_.

Hey! Where are the docs
=======================

As above written, this package is at an early stage of development, and
writing a cool doc with an API and features that may change before the first
beta release is a waste of time.

Meanwhile, you may read and play with the code that's in the ``sandbox/``
directory that explores most features of the provided resources.

Developer notes
===============

Please use a virtualenv to maintain this package, but I should not need to say
that.

Grab the source from the SCM repository
---------------------------------------

.. code:: console

   $ git clone https://github.com/glenfant/mllib.git
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

Build the Sphinx documentation
------------------------------

.. code:: console

   $ python setup.py build_sphinx
   $ firefox build/sphinx/html/index.html

Contributing
============

- Register to `Github <https://github.com/>`_ if not already done.

- Please file a ticket at the `Github tracker
  <https://github.com/glenfant/stopit/issues>`_ that explains your feature or
  improvement.

- Fork the project in your personal repository

- Do the job

- Always check the existing unit tests (see above) and add unit tests that
  verify your feature or bugfix.

- Prefer "git rebase" to "git merge" when synching with the original master.
  See the worflow explained at http://blog.bigbinary.com/2013/09/13/how-to-keep-your-fork-uptodate.html

- Issue a pull request when you're done, mentioning the original ticket you
  created at step 2.

- Don't forget to "star" the project on Github if you like it. ;)

Links
=====

Project home page

  https://github.com/glenfant/mllib

Issues tracker

  https://github.com/glenfant/mllib/isues

Credits
=======

The development of this library is sponsored by the `Assemblée Nationale
<http://www.assemblee-nationale.fr/>`_ (France's Chamber of Deputies).

- Project leader : `Gilles Lenfant <mailto:gilles.lenfant@gmail.com>`_

License
=======

This software is distributed under the terms of the `MIT license
<http://opensource.org/licenses/MIT>`_.
