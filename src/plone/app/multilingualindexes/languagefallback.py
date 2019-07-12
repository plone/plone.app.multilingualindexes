# -*- coding: utf-8 -*-
from Acquisition import aq_base
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from BTrees.OOBTree import OOTreeSet
from logging import getLogger
from plone import api
from plone.app.multilingual.events import ITranslationRegisteredEvent
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingualindexes.utils import get_configuration
from plone.indexer.interfaces import IIndexableObject
from Products.CMFCore.indexing import processQueue
from Products.CMFPlone.utils import safe_hasattr
from Products.DateRecurringIndex.index import DateRecurringIndex
from Products.PluginIndexes.common.UnIndex import UnIndex
from Products.ZCatalog.Catalog import Catalog
from ZODB.POSException import ConflictError
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.globalrequest import getRequest

logger = getLogger(__name__)
_marker = set()  # must be an empty set, part of logic below
_REQ_ANNOTAION = "_languagefallback_unindex_docid_to_tg_"


class LanguageFallbackIndex(UnIndex):
    """Index returning objects of a requested language or in its fallback
    """

    meta_type = "LanguageFallbackIndex"
    query_options = []

    manage_options = (
        {"label": "Settings", "action": "manage_main"},
        {"label": "Browse", "action": "manage_browse"},
    )

    manage = manage_main = DTMLFile("www/manageLFBIndex", globals())
    manage_main._setName("manage_main")
    manage_browse = DTMLFile("www/browseIndex", globals())

    def __init__(self, id, ignore_ex=None, call_methods=None, extra=None, caller=None):
        super(LanguageFallbackIndex, self).__init__(
            id,
            ignore_ex=ignore_ex,
            call_methods=call_methods,
            extra=extra,
            caller=caller,
        )
        self.caller = caller

    @property
    def _catalog(self):
        # attention: we're using heuristics here
        if safe_hasattr(self.caller, "uids"):
            return self.caller
        if isinstance(self.caller, Catalog):
            return self.caller
        if safe_hasattr(self.caller, "_catalog"):
            return self.caller._catalog
        raise AttributeError(
            "LanguageFallbackIndex cant work w/o knowing about its catalog"
        )

    def get_primary_languages_of_fallback(self, lang):
        """Iterator returning primary languages for a given fallback
        """
        for primary_lang, fallbacks in get_configuration().items():
            if lang in fallbacks:
                yield primary_lang

    def has_translation_with_higher_prio_fallback(
        self, primary_language, object_language, translations
    ):
        """Check if a translation exists with a higher priority fallback
        """
        fallback_languages = get_configuration()[primary_language]
        for fallback_lang in fallback_languages:
            if fallback_lang == object_language:
                return False
            if fallback_lang in translations:
                return True
        logger.warn(
            "Incomplete configuration, object language '{0}' must be one of the "
            "configured fallback-languages: {1}!".format(
                object_language, fallback_languages
            )
        )
        return False

    def _remove_docid_for_language(self, documentId, language):
        if documentId in self._index.get(language, []):
            self.removeForwardIndexEntry(language, documentId)
        if language in self._unindex[documentId]:
            self._unindex[documentId].remove(language)

    def index_object(
        self, documentId, obj, threshold=None, recursive=True
    ):  # noqa: C901
        res = False
        # Start handling the language of the object itself
        obj_lang = getattr(aq_base(obj), "Language", _marker) or _marker
        if obj_lang is _marker:
            # No language is set, so no fallbacks can be set
            return res
        if callable(obj_lang):
            obj_lang = obj_lang()
        old_obj_langs = self._unindex.get(documentId, _marker)  # marker is empty
        if obj_lang not in old_obj_langs:
            # Document language changed or new doc
            if old_obj_langs is not _marker:
                # Document is not new. Need to remove all fallbacks
                old_obj_langs = list(old_obj_langs)
                for old_lang in old_obj_langs:
                    self.removeForwardIndexEntry(old_lang, documentId)
                    res = 1
                for old_lang in old_obj_langs:
                    try:
                        self._unindex[documentId].remove(old_lang)
                    except ConflictError:
                        raise
                    except Exception:
                        logger.exception(
                            "Should not happen: %s in old_obj_lang was there, "
                            "now it is not, for document: %r",
                            old_lang,
                            documentId,
                        )
                if not len(self._unindex[documentId]):
                    del self._unindex[documentId]
            # Some language was set, so let us store it
            # Overwriting any old fallbacks
            self.insertForwardIndexEntry(obj_lang, documentId)
            self._unindex[documentId] = OOTreeSet([obj_lang])
            res = 1

        # in an index the obj can be wrapped by an indexable obj wrapper.
        # if this is the case, we need the original object.
        wrapped_obj = getattr(obj, "_getWrappedObject", _marker)
        if wrapped_obj is _marker:
            wrapped_obj = obj
        else:
            wrapped_obj = wrapped_obj()
        # get a dict-like of the translations
        tm = ITranslationManager(wrapped_obj, None)
        if tm is None:
            return res
        translations = tm.get_translations()
        translated_langs = list(translations.keys())
        if obj_lang in translated_langs:
            # it can happen, that our index gets called before the Language
            # Index gets called. In that case, our document might not
            # be registered yet as translated langs
            translated_langs.remove(obj_lang)
        # now we iterate over all possible primary languages and check if
        # the current objects language is a possible fallback
        for primary_lang in self.get_primary_languages_of_fallback(obj_lang):
            # Add fallback entry, if all preconditions pass
            if (
                primary_lang in translated_langs
                or self.has_translation_with_higher_prio_fallback(
                    primary_lang, obj_lang, translated_langs
                )
            ):
                # No fallback needed or fallback with higher priority exists:
                # remove fallback entry if exists
                self._remove_docid_for_language(documentId, primary_lang)
                continue
            self.insertForwardIndexEntry(primary_lang, documentId)
            self._unindex[documentId].add(primary_lang)
            res = True
        if not recursive:
            # were done
            return res
        for translated_obj in translations.values():
            if translated_obj is wrapped_obj:
                continue
            translated_path = "/".join(translated_obj.getPhysicalPath())
            translated_uid = self._catalog.uids[translated_path]
            wrapped_translated = getMultiAdapter(
                (translated_obj, self.caller), IIndexableObject
            )
            self.index_object(translated_uid, wrapped_translated, recursive=False)
        return res

    def unindex_object(self, documentId):
        unindexRecord = self._unindex.get(documentId, _marker)
        if unindexRecord is _marker:
            # Document was never indexed. Go home
            return None

        del self._unindex[documentId]

        for record in unindexRecord:
            self.removeForwardIndexEntry(record, documentId)

        tg_idx = self._catalog.getIndex("TranslationGroup")

        # reindex other object in translationgroup
        # the current tg must be available annotated
        annotation = getattr(getRequest(), _REQ_ANNOTAION, None)
        tg = annotation.get(documentId, None) if annotation is not None else None
        if tg is None:
            # annotations are only written on move/rename/delete
            # if this was not hte case we really must have it available
            tg = tg_idx._unindex.get(documentId, None)
            if tg is None:
                # at this point we do not have any TG yet
                return
        # get one out of tg (enough), because index_object is recursive
        tg_obj_uids = set(tg_idx._index.get(tg, set())) - set([documentId])
        if not tg_obj_uids:
            # no other translations available, were done
            return
        # take one of the others in the TG and index it.
        tg_obj_uid = tg_obj_uids.pop()
        tg_obj = self.caller.unrestrictedTraverse(self._catalog.paths[tg_obj_uid])
        self.index_object(tg_obj_uid, tg_obj)


manage_addLFBIndexForm = DTMLFile("www/addLFBIndex", globals())


def manage_addLFBIndex(
    context, indexid, extra=None, REQUEST=None, RESPONSE=None, URL3=None
):
    """Add a DateRecurringIndex
    """
    return context.manage_addIndex(
        indexid,
        "LanguageFallbackIndex",
        extra=extra,
        REQUEST=REQUEST,
        RESPONSE=RESPONSE,
        URL1=URL3,
    )


InitializeClass(DateRecurringIndex)


def fallback_finder(context, row):
    """Operation for plone.app.querystring"""
    return {row.index: api.portal.get_current_language()}


def reindex_languagefallback(event):
    """Object event subscriber to reindex the index 'language_or_fallback'.
    """
    event.object.reindexObject(idxs=["language_or_fallback"])
    if ITranslationRegisteredEvent.providedBy(event):
        event.target.reindexObject(idxs=["language_or_fallback"])
    else:
        event.old_object.reindexObject(idxs=["language_or_fallback"])
    # ensure this is done before any other indexers running
    # processQueue()


def annotate_documentid_to_tg(obj):
    """Annotates a mapping documentid to TG on the request.
    Thus we're able to unindex and reindex all objects in TG correctly
    """
    # get TG of old object
    tg = queryAdapter(obj, ITG)
    if not tg:
        return
    catalog = api.portal.get_tool("portal_catalog")
    rid = catalog.getrid("/".join(obj.getPhysicalPath()))
    request = getRequest()
    annotation = getattr(request, _REQ_ANNOTAION, None)
    if annotation is None:
        annotation = {}
        setattr(request, _REQ_ANNOTAION, annotation)
    annotation[rid] = tg


def annotate_documentid_to_tg_subscriber(obj, event):
    """object event subscriber
    """
    breakpoint()
    annotate_documentid_to_tg(obj)
