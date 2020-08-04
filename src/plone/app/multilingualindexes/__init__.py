# -*- coding: utf-8 -*-
from . import patches  # noqa
from plone.app.querystring import queryparser
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("plone.app.multilingualindexes")

queryparser.PATH_INDICES |= {"tgpath"}


def initialize(context):
    from plone.app.multilingualindexes.languagefallback import (
        LanguageFallbackIndex,  # NOQA
    )
    from plone.app.multilingualindexes.languagefallback import manage_addLFBIndex
    from plone.app.multilingualindexes.languagefallback import manage_addLFBIndexForm

    context.registerClass(
        LanguageFallbackIndex,
        permission="Add Pluggable Index",
        constructors=(manage_addLFBIndexForm, manage_addLFBIndex),
        icon="www/index.gif",
        visibility=None,
    )
