from zope.interface import Interface
from zope.schema import Dict
from zope.schema import List
from zope.schema import Choice
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout


class IMultilingualIndexPanel(Interface):
    fallback_languages = Dict(title=u'Fallbacks',
                              key_type=Choice(
                                  vocabulary='plone.app.vocabularies.SupportedContentLanguages'
                              ),
                              value_type=List()
                              )


class MultilingualIndexControlPanel(RegistryEditForm):
    schema = IMultilingualIndexPanel
    schema_prefix = 'multilingualindex'
    label = u'MultilingualIndexPanel'

MultiLingualIndexPanelView = layout.wrap_form(
    MultilingualIndexControlPanel, ControlPanelFormWrapper)
