# -*- coding: utf-8 -*-
from plone.app.multilingualindexes import utils
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope.interface import Interface
from zope.schema import Text


class IMultilingualIndexPanel(Interface):
    fallback_languages = Text(title=u'Fallbacks (json)',
                              description=u'''Define what languages can be used
                              as fallback languages in search results.
                              This entry must be a valid json dictionary, the
                              key is the language for that you want to define
                              fallbacks, the value a list of languages that may
                              act as fallbacks. There is a validator that
                              validates your input as valid json, there is no
                              validator to check if you declare languages that
                              already exist. Non existing languages are
                              silently ignored.''',
                              constraint=utils.validate_fallback_record_change)


class MultilingualIndexControlPanel(RegistryEditForm):
    schema = IMultilingualIndexPanel
    schema_prefix = 'multilingualindex'
    label = u'MultilingualIndexPanel'

MultiLingualIndexPanelView = layout.wrap_form(
    MultilingualIndexControlPanel, ControlPanelFormWrapper)
