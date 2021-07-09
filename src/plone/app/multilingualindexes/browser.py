from plone.app.contentlisting.interfaces import IContentListing
from plone.app.multilingualindexes.tgpath import tg_path
from Products.CMFCore.utils import getToolByName
from zope.publisher.browser import BrowserView


class TGPathFolderListing(BrowserView):
    def __call__(self, batch=False, b_size=20, b_start=0, orphan=0, **kw):
        query = {}
        query.update(kw)

        query["tgpath"] = {"query": "/".join(tg_path(self.context)), "depth": 1}

        # if we don't have asked explicitly for other sorting, we'll want
        # it by position in parent
        if "sort_on" not in query:
            query["sort_on"] = "getObjPositionInParent"

        # Provide batching hints to the catalog
        if batch:
            query["b_start"] = b_start
            query["b_size"] = b_size + orphan

        catalog = getToolByName(self.context, "portal_catalog")
        results = catalog(query)
        return IContentListing(results)
