==================
Crunch.io API docs
==================

The Crunch API docs are built using the Sphinx_ documentation system.

.. _Sphinx: http://www.sphinx-doc.org/en/stable/index.html

To build the docs::

    virtualenv env
    source env/bin/activate
    pip -r requirements.txt
    cd source
    make html

To view the docs point your web browser to: ``source/_build/html/index.html``
