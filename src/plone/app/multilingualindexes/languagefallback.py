# -*- coding: utf-8 -*-
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from BTrees.OOBTree import OOTreeSet
from logging import getLogger
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingualindexes.utils import get_configuration
from Products.CMFPlone.utils import safe_hasattr
from Products.DateRecurringIndex.index import DateRecurringIndex
from Products.PluginIndexes.common.UnIndex import UnIndex
from Products.ZCatalog.Catalog import Catalog
from ZODB.POSException import ConflictError


logger = getLogger(__name__)
_marker = object()


class LanguageFallbackIndex(UnIndex):
    """Index returning objects of a requested language or in its fallback
    """

    meta_type = 'LanguageFallbackIndex'
    query_options = []

    def __init__(self, id, ignore_ex=None, call_methods=None,
                 extra=None, caller=None):
        UnIndex.__init__(self, id, ignore_ex=None, call_methods=None,
                         extra=None, caller=None)
        self.caller = caller

    @property
    def _catalog(self):
        # attention: we're using heuristics here
        if safe_hasattr(self.caller, 'uids'):
            return self.caller
        elif isinstance(self.caller, Catalog):
            return self.caller
        elif safe_hasattr(self.caller, '_catalog'):
            return self.caller._catalog
        else:
            raise AttributeError(
                'LanguageFallbackIndex cant work w/o knowing about its catalog'
            )

    def getLangsIFallbackFor(self, lang, req):
        retval = []
        for primary_lang, fallbacks in get_configuration(req).items():
            if lang in fallbacks:
                retval.append(primary_lang)
        return retval

    def translationWithHigherFallbackExists(self,
                                            fallback_for_lang,
                                            my_language,
                                            translations,
                                            request):
        for fallback_lang in get_configuration(request)[fallback_for_lang]:
            if fallback_lang == my_language:
                return False
            elif fallback_lang in translations:
                return True
        raise Exception('Programming Error, my_language must be '
                        'one of the fallback_languages')

    def index_object(self, documentId, obj, threshold=None):
        res = 0
        obj_lang = obj.Language or _marker
        old_obj_langs = self._unindex.get(documentId, set())
        if obj_lang not in old_obj_langs:
            if old_obj_langs != set():
                for old_lang in old_obj_langs:
                    self.removeForwardIndexEntry(old_lang, documentId)
                    res = 1
                    try:
                        for old_lang in old_obj_langs:
                            self._unindex[documentId].remove(old_lang)
                        if not len(self._unindex[documentId]):
                            del self._unindex[documentId]
                    except ConflictError:
                        raise
                    except Exception:
                        logger.exception('Should not happen: '
                                         'old_obj_lang was there, now '
                                         'it is not, for document: '
                                         '%r', documentId)
            if obj_lang is not _marker:
                self.insertForwardIndexEntry(obj_lang, documentId)
                self._unindex[documentId] = OOTreeSet([obj_lang])
                res = 1
        if obj_lang is _marker:
            return res
        wrapped_obj = obj._getWrappedObject()
        translated_langs = (ITranslationManager(wrapped_obj)
                            .get_translations().keys())
        translated_langs.remove(obj_lang)
        fallbacks = self.getLangsIFallbackFor(obj.Language, obj.REQUEST)
        for lang in fallbacks:
            if lang in translated_langs:
                self.removeForwardIndexEntry(lang, documentId)
                if lang in self._unindex[documentId]:
                    self._unindex[documentId].remove(lang)
                continue
            if self.translationWithHigherFallbackExists(lang,
                                                        obj_lang,
                                                        translated_langs,
                                                        obj.REQUEST):
                self.removeForwardIndexEntry(lang, documentId)
                if lang in self._unindex[documentId]:
                    self._unindex[documentId].remove(lang)
                continue
            self.insertForwardIndexEntry(lang, documentId)
            self._unindex[documentId].add(lang)
            res = True
        for lang in fallbacks:
            if lang not in translated_langs:
                continue
            if lang not in self._unindex[documentId]:
                continue
            self._unindex[documentId].remove(lang)
            self.removeForwardIndexEntry(lang, documentId)
            res = True
        return res

    def unindex_object(self, documentId):
        unindexRecord = self._unindex.get(documentId, set())
        if unindexRecord == set():
            return None

        if len(unindexRecord) > 1:
            doc_path = self._catalog.paths[documentId]
            doc_to_unindex = self.caller.unrestrictedTraverse(doc_path)
            tm = ITranslationManager(doc_to_unindex)
            translated_docs = tm.get_translations().values()
            if doc_to_unindex in translated_docs:
                translated_docs.remove(doc_to_unindex)
        else:
            translated_docs = []

        for record in unindexRecord:
            self.removeForwardIndexEntry(record, documentId)
        try:
            del self._unindex[documentId]
        except ConflictError:
            raise
        except Exception:
            logger.debug('Attempt to unindex nonexistent document'
                         ' with id %r', documentId, exc_info=True)
        for doc in translated_docs:
            self.caller.reindexObject(doc, idxs=[self.id])

manage_addDRIndexForm = DTMLFile('www/addDRIndex', globals())


def manage_addDRIndex(
    context,
    indexid,
    extra=None,
    REQUEST=None,
    RESPONSE=None,
    URL3=None
):
    """Add a DateRecurringIndex
    """
    return context.manage_addIndex(
        indexid,
        'LanguageFallbackIndex',
        extra=extra,
        REQUEST=REQUEST,
        RESPONSE=RESPONSE,
        URL1=URL3
    )

InitializeClass(DateRecurringIndex)
