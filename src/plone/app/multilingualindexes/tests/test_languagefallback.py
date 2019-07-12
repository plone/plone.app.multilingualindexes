# -*- coding: utf-8 -*-
from plone import api
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingualindexes.testing import PAMI_FUNCTIONAL_TESTING
from Products.CMFPlone.utils import safe_text

import json
import unittest


class TestLFB(unittest.TestCase):
    """Test that plone.app.multilingualindexes tgpath works."""

    layer = PAMI_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.index = self.portal.portal_catalog.Indexes["language_or_fallback"]
        self.set_config(dict(ca=[], en=[], es=[]))

    def make_obj(self, lang, title="Test"):
        doc = api.content.create(
            container=self.portal[lang], type="Document", title=title
        )
        doc.reindexObject()
        return doc

    def search(self, lang):
        return [
            x.getPath()
            for x in api.content.find(
                context=self.portal, SearchableText="Test", language_or_fallback=lang
            )
        ]

    def set_config(self, config):
        jsondata = json.dumps(dict(config))
        api.portal.set_registry_record(
            "multilingualindex.fallback_languages", safe_text(jsondata)
        )

    def test_case_1(self):
        """
        No fallbacks
        """
        self.make_obj("ca")
        self.assertEqual(1, len(self.search("ca")))
        self.assertEqual(0, len(self.search("es")))
        self.assertEqual(0, len(self.search("en")))

    def test_case_2(self):
        """
        1 Fallback
        """
        self.set_config(dict(ca=["en"], en=[], es=[]))
        self.make_obj("en")
        self.assertEqual(1, len(self.search("ca")))

    def test_case_3(self):
        """
        Documents are same but not identified as same
        """
        self.set_config(dict(ca=["en"], en=[], es=[]))
        self.make_obj("en")
        self.make_obj("ca")
        self.assertEqual(2, len(self.search("ca")))
        self.assertEqual(1, len(self.search("en")))

    def test_case_4(self):
        """
        Documents are same
        """
        self.set_config(dict(ca=["en"], en=[], es=[]))
        en_obj = self.make_obj("en")
        ca_obj = self.make_obj("ca")
        tm = ITranslationManager(ca_obj)
        tm.register_translation("en", en_obj)
        self.assertEqual(1, len(self.search("ca")))
        self.assertEqual(1, len(self.search("en")))

    def test_case_5(self):
        """
        Documents become the same, later
        """
        self.set_config(dict(ca=["en"], en=[], es=[]))
        en_obj = self.make_obj("en")
        ca_obj = self.make_obj("ca")
        self.assertEqual(2, len(self.search("ca")))
        self.assertEqual(1, len(self.search("en")))
        ITranslationManager(ca_obj).register_translation("en", en_obj)
        self.assertEqual(1, len(self.search("ca")))
        self.assertEqual(1, len(self.search("en")))

    def test_case_6(self):
        """
        Do we leave no residue in index on deletion
        """
        self.set_config(dict(ca=["en"], en=[], es=[]))
        # english portal gets reindexed on object creation
        # so we add it to the empty index too
        self.portal.en.reindexObject()
        # also check we have no ca, this also flushes catalog queue
        self.assertEqual(0, len(self.search("ca")))
        # check precondition
        index_keys = dict(self.index._index).keys()
        unindex_keys = dict(self.index._unindex).keys()
        unindex_values = [list(self.index._unindex[x]) for x in self.index._unindex]
        self.assertEqual(0, len(self.search("ca")))
        doc = self.make_obj("en")
        self.assertEqual(1, len(self.search("ca")))
        api.content.delete(doc)
        self.assertEqual(0, len(self.search("ca")))
        self.assertEqual(index_keys, dict(self.index._index).keys())
        self.assertEqual(unindex_keys, dict(self.index._unindex).keys())
        self.assertEqual(
            unindex_values, [list(self.index._unindex[x]) for x in self.index._unindex]
        )

    def test_case_7_1(self):
        """
        What is the desired behavior with two fallbacks
        """
        self.set_config(dict(ca=["en", "es"], en=[], es=[]))
        en_obj = self.make_obj("en")
        es_obj = self.make_obj("es")
        ITranslationManager(en_obj).register_translation("es", es_obj)
        self.assertEqual(["/plone/en/test"], self.search("ca"))
        api.content.delete(en_obj)
        self.assertEqual(["/plone/es/test"], self.search("ca"))
        self.assertEqual(1, len(self.search("ca")))

    def test_case_7_2(self):
        """
        What is the desired behavior with two fallbacks
        (Swap the register translation)
        """
        self.set_config(dict(ca=["en", "es"], en=[], es=[]))
        en_obj = self.make_obj("en")
        es_obj = self.make_obj("es")
        ITranslationManager(es_obj).register_translation("en", en_obj)
        self.assertEqual(["/plone/en/test"], self.search("ca"))
        api.content.delete(en_obj)
        self.assertEqual(["/plone/es/test"], self.search("ca"))
        self.assertEqual(1, len(self.search("ca")))

    def test_case_8_1(self):
        """
        No fallback needed any more
        """
        self.set_config(dict(ca=["en"], en=[], es=[]))
        en_obj = self.make_obj("en")
        self.assertEqual(["/plone/en/test"], self.search("ca"))
        ca_obj = self.make_obj("ca")
        ITranslationManager(en_obj).register_translation("ca", ca_obj)
        self.assertEqual(["/plone/ca/test"], self.search("ca"))

    def test_case_8_2(self):
        """
        No fallback needed any more
        (Swap the register translation)
        """
        self.set_config(dict(ca=["en"], en=[], es=[]))
        en_obj = self.make_obj("en")
        self.assertEqual(1, len(self.search("ca")))
        ca_obj = self.make_obj("ca")
        ITranslationManager(ca_obj).register_translation("en", en_obj)
        self.assertEqual(["/plone/ca/test"], self.search("ca"))
