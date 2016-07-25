# -*- coding: utf-8 -*-
from plone.app.querystring.interfaces import IQueryModifier
from zope.interface import provider

import logging


logger = logging.getLogger(__name__)


PATH_MAP = {  # normal path to tg path
    'plone.app.querystring.operation.string.path':
        'plone.app.querystring.operation.string.pathTG',
    'plone.app.querystring.operation.string.absolutePath':
        'plone.app.querystring.operation.string.absolutePathTG',
    'plone.app.querystring.operation.string.relativePath':
        'plone.app.querystring.operation.string.relativePathTG',
}


def _index_of_criteria(query, name):
    for idx, criteria in enumerate(query):
        if criteria['i'] == name:
            return idx


def _remove_criteria_by_index_name(query, name):
    remove_idx = _index_of_criteria(query, name)
    if remove_idx is not None:
        del query[remove_idx]


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
        # nothing to do here
        return query

    has_path_criteria = any(
        (criteria['i'] == 'path')
        for criteria in query
    )
    if has_path_criteria:
        # if we have a path criteria it is replaced here by a tgpath
        if has_tgpath_criteria:
            _remove_criteria_by_index_name(query, 'tgpath')
        idx_criteria = _index_of_criteria(query, 'path')
        new_criteria = dict(query[idx_criteria])
        new_criteria['i'] = 'tgpath'
        if new_criteria['o'] in PATH_MAP:
            new_criteria['o'] = PATH_MAP[new_criteria['o']]
        query[idx_criteria] = new_criteria
    elif has_tgpath_criteria:
        _remove_criteria_by_index_name(query, 'tgpath')

    # always set path to the portal root in order to prevent the default query
    # modifier to set the path to the navigation root
    query.append({
        'i': 'path',
        'o': 'plone.app.querystring.operation.string.absolutePath',
        'v': '/',
    })
    return query
