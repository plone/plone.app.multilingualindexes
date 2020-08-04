# -*- coding: utf-8 -*-
from Products.CMFCore import indexing
from Products.CMFCore.interfaces import IIndexQueueProcessor
from Products.CMFCore.interfaces import InvalidQueueOperation
from zope.component import getSiteManager


# see https://github.com/zopefoundation/Products.CMFCore/issues/79


def process_patched(self):
    self.optimize()
    if not self.queue:
        return 0
    sm = getSiteManager()
    utilities = list(sm.getUtilitiesFor(IIndexQueueProcessor))
    processed = 0
    for name, util in utilities:
        util.begin()
    # ??? must the queue be handled independently for each processor?
    while self.queue:
        op, obj, attributes, metadata = self.queue.pop(0)
        for name, util in utilities:
            if op == indexing.INDEX:
                util.index(obj, attributes)
            elif op == indexing.REINDEX:
                util.reindex(obj, attributes, update_metadata=metadata)
            elif op == indexing.UNINDEX:
                util.unindex(obj)
            else:
                raise InvalidQueueOperation(op)
        processed += 1
    indexing.debug("finished processing %d items...", processed)
    self.clear()
    return processed


# patch
indexing.IndexQueue.process = process_patched
