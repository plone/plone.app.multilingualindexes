.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==============================================================================
plone.app.multilingualindexes
==============================================================================

Indexes optimized to query multilingual content made with plone.app.multilingual.

Features
--------

``tgpath``
    Utility and index to get the path of an item as UUIDs of its translationgroup.

fallback ``language`` drop-in index
    Index to query items and get fallbacks if not available in the current language.
    Fallbacks can be configured in control-panel and are stored in the registry.


Documentation
-------------

Full documentation for end users can be found in the "docs" folder, and is also available online at http://docs.plone.org/foo/bar


Installation
------------

Install plone.app.multilingualindexes by adding it to your buildout::

    [buildout]

    ...

    eggs =
        plone.app.multilingualindexes


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/plone/plone.app.multilingualindexes/issues
- Source Code: https://github.com/plone/plone.app.multilingualindexes


License
-------

The project is licensed under the GPLv2.
