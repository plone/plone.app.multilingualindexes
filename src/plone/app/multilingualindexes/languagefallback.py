# -*- coding: utf-8 -*-
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from logging import getLogger
from plone.app.multilingual.interfaces import ITranslationManager
from Products.PluginIndexes.common.UnIndex import UnIndex
from Products.PluginIndexes.common.util import parseIndexRequest
from Products.ZCatalog.Catalog import Catalog


logger = getLogger(__name__)
_marker = object()


def get_configuration():
    return {
        'de': ['en', 'it'],
        'it': ['en', 'de'],
        'en': ['de', 'it'],
        'zh': ['en'],
    }


class LanguageFallbackIndex(UnIndex):
    """Index returning objects of a requested language or in its fallback
    """

    meta_type = 'LanguageFallbackIndex'

    def __init__(self, id, ignore_ex=None, call_methods=None,
                 extra=None, caller=None):
        UnIndex.__init__(self, id, ignore_ex=None, call_methods=None,
                         extra=None, caller=None)
        self.caller = caller

    @property
    def _catalog(self):
        # attention: we're using heuristics here
        if hasattr(self.caller, 'uids') or isinstance(self.caller, Catalog):
            return self.caller
        elif hasattr(self.caller, '_catalog'):
            return self.caller._catalog
        else:
            raise AttributeError(
                'LanguageFallbackIndex cant work w/o knowing about its catalog'
            )

    def _iterate_translation_fallbacks(self, context, callback):
        status = 0
        tm = ITranslationManager(context, None)
        if not tm:
            # looks like this one is not translatable
            return status
        translated = tm.get_translated_languages()
        for main_lang, fallbacks in get_configuration().items():
            found = None
            for cur_lang in [main_lang] + fallbacks:
                if cur_lang in translated:
                    found = cur_lang
            if not found:
                continue
            lang_obj = tm.get_translation(found)
            uid_path = '/'.join(lang_obj.getPhysicalPath())
            lang_doc_id = self._catalog.uids[uid_path]
            callback(main_lang, lang_doc_id)

    def index_object(self, documentId, obj, threshold=None):
        """index an object, normalizing the indexed value to an integer
        """

        def indexer_cb(main_lang, lang_doc_id):
            # the unindex contains the information which doc_id was found the
            # last time for the given language
            old_lang_doc_id = self._unindex.get(
                (documentId, main_lang),
                _marker
            )
            if old_lang_doc_id == lang_doc_id:
                return 0

            self._unindex[(documentId, main_lang)] = lang_doc_id
            self.removeForwardIndexEntry(main_lang, old_lang_doc_id)
            self.insertForwardIndexEntry(main_lang, lang_doc_id)
            return 1

        return self._iterate_translation_fallbacks(obj, indexer_cb)

    def unindex_object(self, documentId):
        """ Carefully unindex the object with integer id 'documentId'
        """
        metadata = self._catalog.data[documentId]

        def unindexer_cb(main_lang, lang_doc_id):
            pass

        return self._iterate_translation_fallbacks(obj, unindexer_cb)


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
