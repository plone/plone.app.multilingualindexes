Changelog
=========

2.0 (2019-07-12)
----------------

- Patch CMFCore because of https://github.com/zopefoundation/Products.CMFCore/issues/79
  [jensens]

- Fix bugs on rename/move/delete (wrong fallbacks)
  [jensens]

- Drop support of Plone 5.1
  [jensens]

- Python 3 compatibility
  [jensens]

- Refactor index to be less complex on indexing.
  [jensens]

- Bugfix: Use latest plone.app.multilingual and add subscribers to ensure in-/rein-/unindexing.
  [jensens]

- Fixing "RuntimeError: the bucket being iterated changed size" (issue #3)
  [gogobd]

- Depend on ``Products.CMFPlone`` instead of ``Plone`` to not fetch unnecessary dependencies.
  [thet]


1.0 (2016-10-15)
----------------

- Initial release.
  [jensens]
