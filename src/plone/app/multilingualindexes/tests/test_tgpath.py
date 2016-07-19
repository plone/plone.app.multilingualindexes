# -*- coding: utf-8 -*-
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingualindexes.testing import PAMI_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from zope.interface import alsoProvides

import unittest


class TestTGpath(unittest.TestCase):
    """Test that plone.app.multilingualindexes tgpath works."""

    layer = PAMI_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.layer['request'], IPloneAppMultilingualInstalled)

    def test_tg_path_doc_no_trans(self):
        doc = createContentInContainer(
            self.portal['ca'],
            'Document',
            title=u'Test document'
        )
        from plone.app.multilingual.interfaces import ITG
        from plone.app.multilingualindexes.tgpath import tg_path
        self.assertEqual(
            tg_path(doc),
            [
                '',
                'plone',
                ITG(self.portal.en),
                ITG(self.portal.ca['test-document'])
            ]
        )

    def test_tg_path_docs_same(self):
        doc_ca = createContentInContainer(
            self.portal['ca'],
            'Document',
            title=u'Test document'
        )
        from plone.app.multilingual import api
        doc_en = api.translate(doc_ca, 'en')
        from plone.app.multilingualindexes.tgpath import tg_path
        self.assertEqual(
            tg_path(doc_ca),
            tg_path(doc_en),
        )
