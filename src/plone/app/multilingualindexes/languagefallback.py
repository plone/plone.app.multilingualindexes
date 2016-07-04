# -*- coding: utf-8 -*-
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from logging import getLogger
from plone.app.multilingual.interfaces import ITranslationManager
from Products.CMFPlone.utils import safe_hasattr
from Products.DateRecurringIndex.index import DateRecurringIndex
from Products.PluginIndexes.common.UnIndex import UnIndex
from Products.ZCatalog.Catalog import Catalog
from ZODB.POSException import ConflictError


logger = getLogger(__name__)
_marker = object()


CONFIG = {}


def get_configuration():
    global CONFIG
    return CONFIG


def set_configuration(config):
    global CONFIG
    CONFIG = config


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

    def getLangsIFallbackFor(self, lang):
        for primary_lang, fallbacks in get_configuration().items():
            if lang in fallbacks:
                yield primary_lang

    def index_object(self, documentId, obj, threshold=None):
        res = 0
        obj_lang = obj.Language
        old_obj_langs = self._unindex.get(documentId, [])
        if obj_lang not in old_obj_langs:
            if old_obj_langs is not []:
                for old_lang in old_obj_langs:
                    self.removeForwardIndexEntry(old_lang, documentId)
                if obj_lang is _marker:
                    try:
                        for old_lang in old_obj_langs:
                            self._unindex[documentId].pop(old_lang)
                        if len(self._unindex[documentId]):
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
                self._unindex[documentId] = [obj_lang]
            res = 1
        if not obj_lang:
            return res
        wrapped_obj = obj._getWrappedObject()
        translated_langs = set(ITranslationManager(wrapped_obj)
                               .get_translations().keys()) - {obj_lang}
        fallbacks = set(self.getLangsIFallbackFor(obj.Language))
        for lang in fallbacks - translated_langs:
            self.insertForwardIndexEntry(lang, documentId)
            self._unindex[documentId].append(lang)
            res = True
        for lang in fallbacks & translated_langs:
            if lang not in self._unindex[documentId]:
                continue
            self._unindex[documentId].remove(lang)
            self.removeForwardIndexEntry(lang, documentId)
        return res

    def unindex_object(self, documentId):
        unindexRecord = self._unindex.get(documentId, [])
        if unindexRecord is []:
            return None

        for record in unindexRecord:
            self.removeForwardIndexEntry(record, documentId)
        try:
            del self._unindex[documentId]
        except ConflictError:
            raise
        except Exception:
            logger.debug('Attempt to unindex nonexistent document'
                         ' with id %r', documentId, exc_info=True)

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
