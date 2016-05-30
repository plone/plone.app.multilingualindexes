# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.multilingual.interfaces import ITG
from plone.indexer import indexer
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
