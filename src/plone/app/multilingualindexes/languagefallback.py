# -*- coding: utf-8 -*-
from Acquisition import aq_base
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from BTrees.OOBTree import OOTreeSet
from logging import getLogger
from plone import api
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingualindexes.utils import get_configuration
from plone.indexer.interfaces import IIndexableObject
from Products.CMFPlone.utils import safe_hasattr
from Products.DateRecurringIndex.index import DateRecurringIndex
from Products.PluginIndexes.common.UnIndex import UnIndex
from Products.ZCatalog.Catalog import Catalog
from ZODB.POSException import ConflictError
from zope.component import getMultiAdapter


logger = getLogger(__name__)
_marker = object()


class LanguageFallbackIndex(UnIndex):
    """Index returning objects of a requested language or in its fallback
    """

    meta_type = 'LanguageFallbackIndex'
    query_options = []

    manage_options = (
        {'label': 'Settings', 'action': 'manage_main'},
        {'label': 'Browse', 'action': 'manage_browse'},
    )

    manage = manage_main = DTMLFile('www/manageLFBIndex', globals())
    manage_main._setName('manage_main')
    manage_browse = DTMLFile('www/browseIndex', globals())

    def __init__(self, id, ignore_ex=None, call_methods=None,
                 extra=None, caller=None):
        super(LanguageFallbackIndex, self).__init__(
            id,
            ignore_ex=ignore_ex,
            call_methods=call_methods,
            extra=extra,
            caller=caller
        )
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

    def index_object(self, documentId, obj, threshold=None, recursive=True):
        res = False
        # Ensure that Language and TranslationGroup Index get executed first
        for index in ['Language', 'TranslationGroup']:
            res |= self.__parent__.indexes[index].index_object(documentId, obj,
                                                               threshold)
        # Start handling the language of the object itself
        obj_lang = getattr(aq_base(obj), 'Language', _marker) or _marker
        if callable(obj_lang):
            obj_lang = obj_lang()
        old_obj_langs = self._unindex.get(documentId, set())
        if obj_lang not in old_obj_langs:
            # Document language changed or new doc
            if old_obj_langs != set():
                # Document is not new. Need to remove all fallbacks
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
                # Some language was set, so let us store it
                # Overwriting any old fallbacks
                self.insertForwardIndexEntry(obj_lang, documentId)
                self._unindex[documentId] = OOTreeSet([obj_lang])
                res = 1
        if obj_lang is _marker:
            # No language is set, so no fallbacks can be set
            return res
        wrapped_obj = obj._getWrappedObject()
        tm = ITranslationManager(wrapped_obj, None)
        if tm is None:
            return res
        translations = tm.get_translations()
        translated_langs = translations.keys()
        if obj_lang in translated_langs:
            # it can happen, that our index gets called before the Language
            # Index gets called. In that case, our document might not
            # be registered yet as translated langs
            translated_langs.remove(obj_lang)
        fallbacks = self.getLangsIFallbackFor(obj.Language, obj.REQUEST)
        for lang in fallbacks:
            # Add fallback entry, if all preconditions pass
            if lang in translated_langs:
                # No fallback needed, so remove the fallback entry, if
                # exists
                if documentId in self._index.get(lang, []):
                    self.removeForwardIndexEntry(lang, documentId)
                if lang in self._unindex[documentId]:
                    self._unindex[documentId].remove(lang)
                continue
            if self.translationWithHigherFallbackExists(lang,
                                                        obj_lang,
                                                        translated_langs,
                                                        obj.REQUEST):
                # Fallback with higher priority exists, remove fallback entry
                self.removeForwardIndexEntry(lang, documentId)
                if lang in self._unindex[documentId]:
                    self._unindex[documentId].remove(lang)
                continue
            self.insertForwardIndexEntry(lang, documentId)
            self._unindex[documentId].add(lang)
            res = True
        if recursive:
            for translated_obj in translations.values():
                if translated_obj is wrapped_obj:
                    continue
                translated_path = '/'.join(translated_obj.getPhysicalPath())
                translated_uid = self._catalog.uids[translated_path]
                wrapped_translated = getMultiAdapter(
                    (translated_obj, self.caller),
                    IIndexableObject)
                self.index_object(translated_uid, wrapped_translated,
                                  recursive=False)

        return res

    def unindex_object(self, documentId):
        # Ensure that Language and TranslationGroup Index get executed first
        for index in ['Language', 'TranslationGroup']:
            self.__parent__.indexes[index].unindex_object(documentId)
        unindexRecord = self._unindex.get(documentId, set())
        if unindexRecord == set():
            # Document was never indexed. Go home
            return None

        if len(unindexRecord) > 1:
            # Document was being used as fallback in the past
            # Collect all translated objects, as their status
            # needs to be updated
            doc_path = self._catalog.paths[documentId]
            try:
                doc_to_unindex = self.caller.unrestrictedTraverse(doc_path)
            except KeyError:
                # doc_path is no longer valid, this may happen on move/rename
                return
            tm = ITranslationManager(doc_to_unindex, None)
            if tm is None:
                return
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

manage_addLFBIndexForm = DTMLFile('www/addLFBIndex', globals())


def manage_addLFBIndex(
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


def fallback_finder(context, row):
    """Operation for plone.app.querystring"""
    return {row.index: api.portal.get_current_language()}
