==================
Crunch.io API docs
==================

The Crunch API docs are built using the Sphinx_ documentation system.

.. _Sphinx: http://www.sphinx-doc.org/en/stable/index.html

Building the docs::

    virtualenv env
    source env/bin/activate
    pip -r requirements.txt
    cd source
    make html
