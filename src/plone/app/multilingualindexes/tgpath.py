# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone import api
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.multilingual.interfaces import ITG
from plone.indexer import indexer
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import base_hasattr
from zope.interface import Interface


def tg_path(obj):
    parent = aq_parent(aq_inner(obj))
    if parent:
        path = tg_path(parent)
    else:
        path = []
    try:
        # uuid of translation group
        path.append(ITG(obj))
    except TypeError:
        # could not adapt
        try:
            path.append(obj.getId())
        except AttributeError:
            # apps parent is the request container. ignore
            pass

    return path


@indexer(Interface)
def tg_path_indexer(obj, **kw):
    return tuple(tg_path(obj))


def _extract_depth(row):
    # operation helper
    values = row.values
    if '::' not in row.values:
        return values, None
    values, _depth = row.values.split('::', 1)
    try:
        return values, int(_depth)
    except ValueError:
        pass
    return values, None


def _tg_path_by_root(root, context, row):
    # operation helper
    # take care of absolute paths without root
    values, depth = _extract_depth(row)
    target = None
    if '/' not in values:
        # a uid! little nasty thing, we're dealing with paths, why do you
        # appear here?
        cat = api.portal.get_tool(name='portal_catalog')
        brains = cat(UID=values)
        if len(brains):
            target = brains[0].getObject()
    if not target:
        if not values.startswith(root):
            values = root + '/' + values
        target = context.unrestrictedTraverse(values)
    values = '/'.join(tg_path(target))
    query = {}
    if depth is not None:
        query['depth'] = depth
        # when a depth value is specified, a trailing slash matters on the
        # query
        values = values.rstrip('/')
    query['query'] = [values]
    return {row.index: query}


def operation_navigation_tg_path(context, row):
    return _tg_path_by_root(getNavigationRoot(context), context, row)


def operation_absolute_tg_path(context, row):
    root = '/'.join(api.portal.get().getPhysicalPath())
    return _tg_path_by_root(root, context, row)


def operation_relative_tg_path(context, row):
    # Walk through the tree
    values, depth = _extract_depth(row)
    current = context
    for value in values.split('/'):
        if not value:
            continue
        if value == '..':
            if IPloneSiteRoot.providedBy(current):
                break
            parent = aq_parent(current)
            if parent:
                current = parent
        else:
            if base_hasattr(current, value):
                child = getattr(current, value, None)
                if child and base_hasattr(child, 'getPhysicalPath'):
                    current = child

    values = '/'.join(tg_path(current))
    query = {}
    if depth is not None:
        query['depth'] = depth
        values = values.rstrip('/')
    query['query'] = [values]
    return {row.index: query}
