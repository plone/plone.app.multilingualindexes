# -*- coding: utf-8 -*-
from plone import api
from zope.schema._bootstrapinterfaces import ValidationError
import json


def get_configuration(request):
    try:
        return request.plone_app_multilingualindexes_fallbacks
    except AttributeError:
        fallbacks = json.loads(api.portal.get_registry_record(
            'multilingualindex.fallback_languages'))
        setattr(request, 'plone_app_multilingualindexes_fallbacks', fallbacks)
        return fallbacks


class JsonError(ValidationError):
    pass


def validate_fallback_record_change(event):
    if event.record.__name__ != 'multilingualindex.fallback_languages':
        return
    try:
        json.loads(event.newValue)
    except ValueError, e:
        raise JsonError(str(e))
