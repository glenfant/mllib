=============
mllib sandbox
=============

This is a sandbox demo of some features of ``mllib``. Running any demo in this
directory assumes that you own a test ML8 database which access point is
http://localhost:8000, on which a user ``admin`` with password ``admin`` is
granted for any operation on that database, and finally, the associated REST
instance accepts the digest authentication.

In any other case, please provide your custom entry point, credential and
authentication method in the ``MLLIB_TEST_SERVER`` environment variable that
should have the folowing BNF form:

.. code:: text

   mllib_test_server = hostname ":" port ":" username ":" password [ ":" auth_method ];
   auth_method = "basic" | "digest" ;

``digest`` is the default authentication method so you may omit it.

Example:

.. code:: console

   export MLLIB_TEST_SERVER=my-ml-host:8100:manager:xkvr:basic

.. danger::

   The demo scripts may delete or alter any document in the database you use
   for this demo. You have been warned.
