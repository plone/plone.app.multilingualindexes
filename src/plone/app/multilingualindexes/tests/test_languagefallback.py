# -*- coding: utf-8 -*-
from plone import api
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingualindexes.testing import PAMI_FUNCTIONAL_TESTING

import json
import unittest


class TestLFB(unittest.TestCase):
    """Test that plone.app.multilingualindexes tgpath works."""

    layer = PAMI_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.index = self.portal.portal_catalog.Indexes['Language2']
        self.set_config(dict(ca=[], en=[], es=[]))

    def make_obj(self, lang, title='Test'):
        doc = api.content.create(
            container=self.portal[lang],
            type='Document',
            title=title)
        # XX We do a reindex here because an event handler sets Language
        # too late. We could copy that event handler though
        self.portal.portal_catalog.reindexObject(doc)
        return doc

    def search(self, lang):
        return [x.getPath() for x in api.content.find(context=self.portal,
                                                      SearchableText='Test',
                                                      Language2=lang)]

    def set_config(self, config):
        api.portal.set_registry_record(
            'multilingualindex.fallback_languages',
            json.dumps(dict(config)).decode('utf-8'))

    def test_case_1(self):
        """
        No fallbacks
        """
        self.make_obj('ca')
        self.assertEqual(1, len(self.search('ca')))
        self.assertEqual(0, len(self.search('es')))
        self.assertEqual(0, len(self.search('en')))

    def test_case_2(self):
        """
        1 Fallback
        """
        self.set_config(dict(ca=['en'], en=[], es=[]))
        self.make_obj('en')
        self.assertEqual(1, len(self.search('ca')))

    def test_case_3(self):
        """
        Documents are same but not identified as same
        """
        self.set_config(dict(ca=['en'], en=[], es=[]))
        self.make_obj('en')
        self.make_obj('ca')
        self.assertEqual(2, len(self.search('ca')))
        self.assertEqual(1, len(self.search('en')))

    def test_case_4(self):
        """
        Documents are same
        """
        self.set_config(dict(ca=['en'], en=[], es=[]))
        en_obj = self.make_obj('en')
        ca_obj = self.make_obj('ca')
        ITranslationManager(ca_obj).register_translation('en', en_obj)
        self.assertEqual(1, len(self.search('ca')))
        self.assertEqual(1, len(self.search('en')))

    def test_case_5(self):
        """
        Documents become the same, later
        """
        self.set_config(dict(ca=['en'], en=[], es=[]))
        en_obj = self.make_obj('en')
        ca_obj = self.make_obj('ca')
        self.assertEqual(2, len(self.search('ca')))
        self.assertEqual(1, len(self.search('en')))
        ITranslationManager(ca_obj).register_translation('en', en_obj)
        self.assertEqual(1, len(self.search('ca')))
        self.assertEqual(1, len(self.search('en')))

    def test_case_6(self):
        """
        Do we leave no residue in index on deletion
        """
        self.set_config(dict(ca=['en'], en=[], es=[]))
        # english portal gets reindexed on object creation
        # so we add it to the empty index too
        self.portal.portal_catalog.reindexObject(self.portal.en)
        index = dict(self.index._index)
        unindex = dict(self.index._unindex)
        doc = self.make_obj('en')
        self.assertEqual(1, len(self.search('ca')))
        api.content.delete(doc)
        self.assertEqual(0, len(self.search('ca')))
        self.assertEqual(index, dict(self.index._index))
        self.assertEqual(unindex.keys(), dict(self.index._unindex).keys())

        def listify(treeset):
            return [list(x) for x in treeset]
        self.assertEqual(listify(unindex.values()),
                         listify(dict(self.index._unindex).values()))

    def test_case_7(self):
        """
        What is the desired behavior with two fallbacks
        """
        self.set_config(dict(ca=['en', 'es'], en=[], es=[]))
        en_obj = self.make_obj('en')
        es_obj = self.make_obj('es')
        ITranslationManager(en_obj).register_translation('es', es_obj)
        self.portal.portal_catalog.reindexObject(es_obj)
        self.portal.portal_catalog.reindexObject(en_obj)
        self.assertEqual(['/plone/en/test'], self.search('ca'))
        api.content.delete(en_obj)
        self.assertEqual(['/plone/es/test'], self.search('ca'))
        self.assertEqual(1, len(self.search('ca')))

    def test_case_8(self):
        """
        No fallback needed any more
        """
        self.set_config(dict(ca=['en'], en=[], es=[]))
        en_obj = self.make_obj('en')
        self.assertEqual(1, len(self.search('ca')))
        ca_obj = self.make_obj('ca')
        # I think it is a bug that register Translation does not index
        # both objects.
        ITranslationManager(en_obj).register_translation('ca', ca_obj)
        self.portal.portal_catalog.reindexObject(ca_obj)
        self.portal.portal_catalog.reindexObject(en_obj)
        self.assertEqual(['/plone/ca/test'], self.search('ca'))
