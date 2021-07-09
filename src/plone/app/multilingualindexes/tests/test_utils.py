from plone import api
from plone.app.multilingualindexes.testing import PAMI_FUNCTIONAL_TESTING
from plone.app.multilingualindexes.utils import get_configuration
from zope.schema._bootstrapinterfaces import ValidationError

import unittest


class TestUtils(unittest.TestCase):
    """Test that plone.app.multilingualindexes tgpath works."""

    layer = PAMI_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_get_fallbacks(self):
        class FakeRequest:
            pass

        request = FakeRequest()
        self.assertEqual({"de": ["en"], "en": ["de"]}, get_configuration(request))

    def test_set_bad_fallbacks(self):
        self.assertRaises(
            ValidationError,
            api.portal.set_registry_record,
            "multilingualindex.fallback_languages",
            "[[[[[",
        )

    def test_get_fallbacks_caches(self):
        class FakeRequest:
            pass

        request = FakeRequest()
        api.portal.set_registry_record(
            "multilingualindex.fallback_languages", '{"fr": []}'
        )
        self.assertEqual({"fr": []}, get_configuration(request))
        api.portal.set_registry_record(
            "multilingualindex.fallback_languages", '{"pt": ["es"]}'
        )
        # It will be impossible for a user to change the configuration
        # and some content in one request. This is why we cache
        # the configuration on the request object and this is
        # why the change above wasn't reflected here.
        self.assertEqual({"fr": []}, get_configuration(request))
        # For fun:
        request = FakeRequest()
        self.assertEqual({"pt": ["es"]}, get_configuration(request))
