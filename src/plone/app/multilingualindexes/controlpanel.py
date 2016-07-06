# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope.interface import Interface
from zope.schema import Text


class IMultilingualIndexPanel(Interface):
    fallback_languages = Text(title=u'Fallbacks (json)')


class MultilingualIndexControlPanel(RegistryEditForm):
    schema = IMultilingualIndexPanel
    schema_prefix = 'multilingualindex'
    label = u'MultilingualIndexPanel'

MultiLingualIndexPanelView = layout.wrap_form(
    MultilingualIndexControlPanel, ControlPanelFormWrapper)
