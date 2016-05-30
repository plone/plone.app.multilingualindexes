# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.multilingualindexes.testing import PAMI_INTEGRATION_TESTING

import unittest


class TestSetup(unittest.TestCase):
    """Test that plone.app.multilingualindexes is properly installed."""

    layer = PAMI_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if plone.app.multilingualindexes is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'plone.app.multilingualindexes'))

    def test_browserlayer(self):
        """Test that IPloneAppMultilingualindexesLayer is registered."""
        from plone.app.multilingualindexes.interfaces import (
            IPloneAppMultilingualindexesLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IPloneAppMultilingualindexesLayer,
            utils.registered_layers()
        )


class TestUninstall(unittest.TestCase):

    layer = PAMI_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['plone.app.multilingualindexes'])

    def test_product_uninstalled(self):
        """Test if plone.app.multilingualindexes is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'plone.app.multilingualindexes'))

    def test_browserlayer_removed(self):
        """Test that IPloneAppMultilingualindexesLayer is removed."""
        from plone.app.multilingualindexes.interfaces import (
            IPloneAppMultilingualindexesLayer)
        from plone.browserlayer import utils
        self.assertNotIn(
            IPloneAppMultilingualindexesLayer,
            utils.registered_layers()
        )
