# -*- coding: utf-8 -*-
from plone.app.querystring.interfaces import IQueryModifier
from zope.interface import provider

import logging


logger = logging.getLogger(__name__)


@provider(IQueryModifier)
def modify_query_to_enforce_site_root(query):
    """enforce a search in the current navigation root

    if a tgpath or language_or_fallback was given, we search global.
    this prevents later navigation root stickyness.
    """
    if not query:
        return query

    query = list(query)

    has_tgpath_criteria = any(
        (criteria['i'] == 'tgpath')
        for criteria in query
    )
    has_lof_criteria = any(
        (criteria['i'] == 'language_or_fallback')
        for criteria in query
    )

    if not (has_lof_criteria or has_tgpath_criteria):
        return query

    has_path_criteria = any(
        (criteria['i'] == 'path')
        for criteria in query
    )
    if has_path_criteria:
        # current criteria combination does not make sense: remove criteria
        remove_idx = None
        for idx, criteria in enumerate(query):
            if criteria['i'] == 'path':
                remove_idx = idx
        if remove_idx is not None:
            del query[remove_idx]

    query.append({
        'i': 'path',
        'o': 'plone.app.querystring.operation.string.absolutePath',
        'v': '/',
    })
    return query
