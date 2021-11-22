Changelog
=========

3.0.2 (2021-11-22)
------------------

- Make request caching more test friendly (where there is no request). [jensens]


3.0.1 (2021-11-17)
------------------

- Fix import for Plone 6 and add CI [jensens]


3.0.0 (2021-11-16)
------------------

- Drop Python 2 Support [jensens]

- Switch CI to GitHub Actions.
  [gogobd]

- InitializeClass has moved, fixing issue https://github.com/plone/plone.app.multilingualindexes/issues/13
  [gogobd]


2.1 (2020-08-04)
----------------

- Patch that allows for using multiple paths, fixing issue https://github.com/plone/plone.app.multilingualindexes/issues/9
  [gogobd]
- User PATH_INDICES as suggested by jensens
  [gogobd]


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
