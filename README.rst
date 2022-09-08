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
are usable by ``doit`` for task definition. Furthermore, utilities for
e.g., commonly used (by me) file dependency searching are included.

Usage
-----

A typical ``doit`` task definition file (i.e., ``dodo.py``) could have
the following contents:

.. code:: python

   def task_create_data():
       """
       Create data.txt file.
       """
       return {
           # This task depends on a python file, create_data.py
           # It will be rerun when create_data.py is modified
           "file_dep": ["create_data.py"],
           "actions": ["python create_data.py"],
           "targets": ["data.txt"],
       }


   def task_build():
       """
       Run a python source file that takes a data.txt file argument.

       After running the source file, an output file is created
       (``output.file``).
       """
       return {
           # This task depends on two files and will be re-run if
           # either changes
           "file_dep": ["source_file.py", "data.txt"],
           # This task depends on another task
           # When create_data is re-run, so is this task
           # Furthermore, this task is always ran after create_data task
           "task_dep": ["create_data"],
           "actions": ["python source_file.py data.txt"],
           "targets": ["output.file"],
       }

There is a lot of boilerplate and code reuse to do here. All paths to
files could be defined outside the functions. This applies to both data
files and target files. Furthermore, the ``task_dep`` is defined using a
string even though it could be extracted programmatically from the
``task_create_data`` function object.

With ``doit-ext``, and with maximizing code reuse, these tasks could be
defined as such:

.. code:: python

   from doit_ext.compose import ComposeTask

   # pathlib.Path is recommended and accepted by doit
   # for any file inputs (file deps, targets, etc.)
   CREATE_DATA_PY = "create_data.py"
   DATA_TXT = "data.txt"
   SOURCE_FILE_PY = "source_file.py"
   OUTPUT_FILE = "output.file"


   def task_create_data():
       composed_task = (
           compose.ComposeTask()
           .add_file_deps(CREATE_DATA_PY)
           .add_actions(f"python {CREATE_DATA_PY}")
           .add_targets(DATA_TXT)
       )
       return composed_task.compile()


   def task_build():
       composed_task = (
           compose.ComposeTask()
           .add_file_deps(SOURCE_FILE_PY, DATA_TXT)
           .add_task_deps(task_create_data)
           .add_actions(f"python {SOURCE_FILE_PY} {DATA_TXT}")
           .add_targets(OUTPUT_FILE)
       )
       return composed_task.compile()

Whether this type of defining tasks looks more appealing to you is
subjective. The ``doit`` interface is excellent in its simplicity but
personally I believe it leaves a great amount of possibilities for
mistakes in the task definitions. This is especially the case for
`config_changed <https://pydoit.org/uptodate.html#config-changed>`__
options. In ``doit_ext`` ``config_changed`` dependencies
can be added as such:

.. code:: python

   def task_with_config_deps():
       composed_task = (
           compose.ComposeTask()
           .add_config_dependency(dict(x=2))
           .add_config_dependency(dict(y=2))
       )
       return composed_task.compile()

These dictionaries will be handled and merged behind the scenes and the
output task definition should be understood by ``doit`` as expected. You
can print out the compiled task (``print(composed_task.compile())``)
to check and verify the contents.

Installation
------------

.. code:: bash

   pip install doit-ext

This package will only depend on ``doit``. Furthermore, no modification
of e.g., the ``doit`` command-line command is done and no functionality
of ``doit`` is modified. This package merely adds useful utilities to be
used with ``doit`` if wanted.

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
