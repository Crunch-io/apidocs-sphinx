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

Deploying docs to production
----------------------------

Most changes should go through the official release process. Not someone pushing MERGE manually on a PR.

However, if you have a good reason to do so: If you manually merge a PR in github, it will merge into master. Travis will initiate the build of the docs from master and push those to github pages, which will push it to production.

Proper Reference Links
----------------------

If you use the correct Sphinx features for creating internal references in the
doc, then Sphinx will check the links at build time and report broken links
automatically. Also, the links will work between files, and keep working even
if section header names are modified.

Example:

To create a link target for a document section::

    .. _my-link-label:

    Section Title
    =============

    Section content. Blah blah.

To create a reference to this section from anywhere in the docs::

    For further information, see :ref:`this section <my-link-label>`.

The link title will be "this section", and it will point to the section labeled
with ``my-link-label``.

For further details, see: `Sphinx cross-referencing syntax
<http://www.sphinx-doc.org/en/stable/markup/inline.html#cross-referencing-syntax>`__

(P.S. The source for the paragraph above in README.rst is an example of how to
do external links.)
