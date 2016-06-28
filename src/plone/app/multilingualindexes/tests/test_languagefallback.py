# -*- coding: utf-8 -*-
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingualindexes.testing import PAMI_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from zope.interface import alsoProvides

import unittest


class TestLFB(unittest.TestCase):
    """Test that plone.app.multilingualindexes tgpath works."""

    layer = PAMI_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
