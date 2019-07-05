# -*- coding: utf-8 -*-
from plone.app.multilingual.testing import PLONE_APP_MULTILINGUAL_PRESET_FIXTURE  # noqa
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneWithPackageLayer
from plone.testing import z2

import plone.app.multilingualindexes


PAMI_FIXTURE = PloneWithPackageLayer(
    bases=(PLONE_APP_MULTILINGUAL_PRESET_FIXTURE,),
    name="PAMILayer:Fixture",
    gs_profile_id="plone.app.multilingualindexes:default",
    zcml_package=plone.app.multilingualindexes,
    zcml_filename="configure.zcml",
    additional_z2_products=["plone.app.multilingualindexes"],
)


PAMI_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAMI_FIXTURE,), name="PAMILayer:IntegrationTesting"
)


PAMI_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PAMI_FIXTURE,), name="PAMILayer:FunctionalTesting"
)


PAMI_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(PAMI_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PAMILayer:AcceptanceTesting",
)
