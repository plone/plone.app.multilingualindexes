# -*- coding: utf-8 -*-
from plone.app.querystring.interfaces import IQueryModifier
from zope.interface import provider

import logging


logger = logging.getLogger(__name__)


PATH_MAP = {  # normal path to tg path
    "plone.app.querystring.operation.string.path": "plone.app.querystring.operation.string.pathTG",  # noqa
    "plone.app.querystring.operation.string.absolutePath": "plone.app.querystring.operation.string.absolutePathTG",  # noqa
    "plone.app.querystring.operation.string.relativePath": "plone.app.querystring.operation.string.relativePathTG",  # noqa
}


def _indices_of_criteria(query, name):
    return [idx for idx, criteria in enumerate(query) if criteria["i"] == name]


def _remove_criteria_by_index_name(query, name):
    remove_idxs = _indices_of_criteria(query, name)
    return [i for idx, i in enumerate(query) if idx not in remove_idxs]


@provider(IQueryModifier)
def modify_query_to_enforce_site_root(query):
    """enforce a search in the current navigation root

    if a tgpath or language_or_fallback was given, we search global.
    this prevents later navigation root stickyness.
    """
    if not query:
        return query

    query = list(query)

    has_tgpath_criteria = any((criteria["i"] == "tgpath") for criteria in query)
    has_lof_criteria = any(
        (criteria["i"] == "language_or_fallback") for criteria in query
    )

    if not (has_lof_criteria or has_tgpath_criteria):
        # nothing to do here
        return query

    has_path_criteria = any((criteria["i"] == "path") for criteria in query)
    if has_path_criteria:
        # if we have a path criteria it is replaced here by a tgpath
        if has_tgpath_criteria:
            query = _remove_criteria_by_index_name(query, "tgpath")
        # Handle multiple paths
        idx_criteria = _indices_of_criteria(query, "path")
        new_criteria = [dict(query[i]) for i in idx_criteria]
        for i in new_criteria:
            i["i"] = "tgpath"
        for i in new_criteria:
            if i["o"] in PATH_MAP:
                i["o"] = PATH_MAP[i["o"]]
        for i, x in enumerate(idx_criteria):
            query[x] = new_criteria[i]
    elif has_tgpath_criteria:
        query = _remove_criteria_by_index_name(query, "tgpath")

    # always set path to the portal root in order to prevent the default query
    # modifier to set the path to the navigation root
    query.append(
        {
            "i": "path",
            "o": "plone.app.querystring.operation.string.absolutePath",
            "v": "/",
        }
    )

    return query
