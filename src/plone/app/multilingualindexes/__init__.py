# -*- coding: utf-8 -*-
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('plone.app.multilingualindexes')


def initialize(context):
    from plone.app.multilingualindexes.languagefallback import LanguageFallbackIndex  # NOQA
    from plone.app.multilingualindexes.languagefallback import manage_addDRIndexForm  # NOQA
    from plone.app.multilingualindexes.languagefallback import manage_addDRIndex  # NOQA

    context.registerClass(
        LanguageFallbackIndex,
        permission='Add Pluggable Index',
        constructors=(manage_addDRIndexForm,
                      manage_addDRIndex
                      ),
        icon='www/index.gif',
        visibility=None
    )
