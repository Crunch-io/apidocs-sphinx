==================
Crunch.io API docs
==================

The Crunch API docs are built using the Sphinx_ documentation system.

.. _Sphinx: http://www.sphinx-doc.org/en/stable/index.html

To build the docs::

    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    make html

To view the docs point your web browser to: ``build/html/index.html``

----------------------------
Deploying docs to production
----------------------------

Most changes should go through the official release process. Not someone pushing MERGE manually on a PR.

However, if you have a good reason to do so: If you manually merge a PR in github, it will merge into master. Travis will initiate the build of the docs from master and push those to github pages, which will push it to production.
