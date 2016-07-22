# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.utils import safe_hasattr
from zope.schema._bootstrapinterfaces import ValidationError

import json


def get_configuration(request):
    try:
        return request._plone_app_multilingualindexes_fallbacks_
    except AttributeError:
        fallbacks = json.loads(
            api.portal.get_registry_record(
                'multilingualindex.fallback_languages'
            )
        )
        setattr(
            request,
            '_plone_app_multilingualindexes_fallbacks_',
            fallbacks
        )
        return fallbacks


class JsonError(ValidationError):
    pass


def validate_fallback_record_change(event_or_data):
    if safe_hasattr(event_or_data, 'record'):
        if (event_or_data.record.__name__ !=
                'multilingualindex.fallback_languages'):
            return
        value_to_check = event_or_data.newValue
    else:
        value_to_check = event_or_data

    try:
        json.loads(value_to_check)
        return True
    except ValueError, e:
        raise JsonError(str(e))
