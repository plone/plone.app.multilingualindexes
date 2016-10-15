.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==============================================================================
plone.app.multilingualindexes
==============================================================================

Indexes optimized to query multilingual content made with plone.app.multilingual.

Features
--------

``tgpath`` Index (Translation Group Path)
    Utility and index to get the path of an item as UUIDs of its translationgroup.

``language_or_fallback`` Index
    Index to query items and get one fallback if not available in the current language.
    Fallbacks can be configured in control-panel and are stored in the registry.

Integration with ``Collections``
    Both indexes are available in Collections and other places using ``plone.app.querystring`` under the hood.
    Both indexes do only need activation.

    ``tgpath`` is available as a switch ``Language independent location``.
    If this is selected, the normal path will be converted to a tgpath!
    If no path is selected this switch has no effect.

    .. figure:: docs/querystring_tgpath.png
       :scale: 100 %
       :alt: Querystring selection with Translationgroup path


    ``language_or_fallback`` is available as ``Fallback languages``.
    If a path is selected together with this option, the path will be converted to a ``tgpath``.

    If the ``tgpath`` or ``language_or_fallback`` is used in a Collection, the ``path`` will be set to the portal.
    Thus the usal automatically added fixation to the current ``INavigationRoot`` wont be set,
    because language root folders are navigation roots.

    .. figure:: docs/querystring_fallback.png
       :scale: 100 %
       :alt: Querystring selection with Language fallback and (optional) location.


Behind the scenes
-----------------

Fallback Index
    It is in fact a simple FieldIndex.
    Fallback detection happens on index time.
    On query time it has the same functionality and performance as the normal Language index.

    .. figure:: docs/index_manage_browse.png
       :scale: 100 %
       :alt: Browse the index to get a feeling what fallbacks are in there.

Translation Group Index
    It is in fact a normal ExtendendPathIndex.
    Just the path it indexes consists out of the translation group uids.
    If an item is not translatable and thus is not part of an translationgroup,
    then its normal id is taken as patyh element.
    Path example: ``/Plone/f5843e426b5d47cdb44af587b322f7ea/320b1ffbf0f64603803043d48bd57516``.

    In order to query the index, you need to use the translationgroup path instead of the id path::

      from plone.app.multilingualindexes.tgpath import tg_path
      import plone.api

      plone.api.content.find(
          tgpath='/'.join(tg_path(context)),
          language_or_fallback=plone.api.portal.get_current_language()
      )


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
