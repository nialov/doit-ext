Documentation
=============

|Documentation Status| |PyPI Status| |CI Test| |Coverage|

Motivation for software
-----------------------

`doit <https://github.com/pydoit/doit>`__ is an excellent package for
creating tasks with e.g., file dependencies and specific targets with
likeness to ``make``. The definition of *tasks*, as they are called in
``doit``, is done by creating a function that returns a dictionary
(``return dict()``) or a generator of dictionaries (``yield dict()``).
This provides a simple interface for creating tasks. However, the
simplicity results in a lot of boilerplate as same file dependencies or
task dependencies are used across different tasks. As the tasks are
defined in ``Python`` code, in a file called ``dodo.py``, there is an
infinite amount of possibilities to reduce this boilerplate and increase
task definition reuse. This package is an attempt at creating a
composeable functional framework for creation of ``doit`` easily
reusable task definitions that are then compiled to dictionaries that
are usable by ``doit`` for task definition.

Running tests
-------------

To run pytest in currently installed environment:

.. code:: bash

   poetry run pytest

To run full extensive test suite:

.. code:: bash

   poetry run doit
   # Add -n <your-cpu-core-count> to execute tasks in parallel
   # E.g.
   poetry run doit -n 8 -v 0
   # -v 0 is added to limit verbosity to mininum (optional)
   # doit makes sure tasks are run in the correct order
   # E.g. if a task uses a requirements.txt file that other task produces
   # the producer is run first even with parallel execution

Formatting and linting
----------------------


Formatting & linting:

.. code:: bash

   poetry run doit pre_commit
   poetry run doit lint

Building docs
-------------

Docs can be built locally to test that ``ReadTheDocs`` can also build them:

.. code:: bash

   poetry run doit docs

doit usage
----------

To list all available commands from ``dodo.py``:

.. code:: bash

   poetry run doit list

Development
~~~~~~~~~~~

Development dependencies for ``doit_ext`` include:

-  ``poetry``
-  ``doit``
-  ``nox``
-  ``copier``
-  ``pytest``
-  ``coverage``
-  ``sphinx``

Big thanks to all maintainers of the above packages!

License
~~~~~~~

Copyright © 2022, Nikolas Ovaskainen.

-----


.. |Documentation Status| image:: https://readthedocs.org/projects/doit-ext/badge/?version=latest
   :target: https://doit-ext.readthedocs.io/en/latest/?badge=latest
.. |PyPI Status| image:: https://img.shields.io/pypi/v/doit-ext.svg
   :target: https://pypi.python.org/pypi/doit-ext
.. |CI Test| image:: https://github.com/nialov/doit-ext/workflows/test-and-publish/badge.svg
   :target: https://github.com/nialov/doit-ext/actions/workflows/test-and-publish.yaml?query=branch%3Amaster
.. |Coverage| image:: https://raw.githubusercontent.com/nialov/doit-ext/master/docs_src/imgs/coverage.svg
   :target: https://github.com/nialov/doit-ext/blob/master/docs_src/imgs/coverage.svg
