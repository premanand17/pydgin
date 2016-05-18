''' Generic documents based on elasticsearch documents. '''
import locale

from django.conf import settings
from django.utils.module_loading import import_string
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query
from elastic.result import Document

from pydgin import pydgin_settings


class PydginDocument(Document):
    ''' A general pydgin feature document (e.g. publication). '''

    @staticmethod
    def factory(hit):
        ''' Factory method for creating types of documents based on
        their elasticsearch index type.
        @type  hit: dict
        @param hit: elasticsearch hit.
        '''
        (idx, idx_type) = ElasticSettings.get_idx_key_by_name(hit['_index'], idx_type_name=hit['_type'])
        if idx is None or idx_type is None:
            return PydginDocument(hit)

        doc_class_str = ElasticSettings.get_label(idx, idx_type, label='class')
        doc_class = import_string(doc_class_str) if doc_class_str is not None else None

        return doc_class(hit) if doc_class is not None else PydginDocument(hit)

    def get_name(self):
        ''' Override get pydgin document name. '''
        raise NotImplementedError("Inheriting class should implement this method")

    def get_sub_heading(self):
        ''' Overridden get feature sub-heading. '''
        raise NotImplementedError("Inheriting class should implement this method")

    def get_diseases(self):
        ''' Overridden get diseases for feature. '''
        if 'criteria' in settings.INSTALLED_APPS:
            return 1
        return 0
        # raise NotImplementedError("Inheriting class should implement this method")


class ResultCardMixin(object):
    ''' Result card object. '''
    EXCLUDED_RESULT_KEYS = []

    def url(self):
        ''' Document page url. '''
        raise NotImplementedError("Inheriting class should implement this method")

    def get_link_id(self):
        ''' Page link id. '''
        return NotImplementedError("Inheriting class should implement this method")

    def is_external(self):
        ''' External document link. '''
        return False

    def comparable(self):
        ''' Document(s) can be compared. '''
        return False

    def result_card_process_attrs(self):
        ''' Override to carry out any processing of document attributes for displaying. '''
        pass

    def result_card_keys(self):
        ''' Gets the keys of the document object as an ordered list to show in the result card. '''
        self.result_card_process_attrs()
        keys = set([k for k in self.__dict__.keys() if k not in self.EXCLUDED_RESULT_KEYS and k is not '_meta'])
        if self.highlight() is not None:
            keys |= set(self.highlight().keys())
        return sorted(list(keys))


class FeatureDocument(PydginDocument, ResultCardMixin):
    ''' A feature (e.g. gene, marker) document. '''

    def get_position(self, build=pydgin_settings.DEFAULT_BUILD):
        '''
        Overridden get feature position by build.
        @type  build: integer
        @keyword build: NCBI build to return position for.
         '''
        return ("chr" + getattr(self, "seqid") +
                ":" + str(locale.format("%d",  getattr(self, "start"), grouping=True)) +
                "-" + str(locale.format("%d", getattr(self, "stop"), grouping=True)))
        # raise NotImplementedError("Inheriting class should implement this method")

    def get_name(self):
        return getattr(self, "name")

    def get_strand_as_int(self):
        '''
        Generic method to return strand of a feature as -1/0/1 nomenclature.
         '''
        if hasattr(self, "strand") and getattr(self, 'strand') is not None:
            strand = getattr(self, 'strand')
            if strand == '+':
                return 1
            if strand == '-':
                return -1
        return 0


class PublicationDocument(PydginDocument, ResultCardMixin):
    ''' Publication document. '''
    EXCLUDED_RESULT_KEYS = ['pmid', 'tags']

    def get_name(self):
        ''' Document name. '''
        return getattr(self, 'pmid')

    def get_link_id(self):
        ''' Page link id. '''
        return self.get_name()

    def url(self):
        ''' Document page url. '''
        return "http://www.ncbi.nlm.nih.gov/pubmed/"

    def is_external(self):
        ''' External document link. '''
        return True

    def result_card_keys(self):
        ''' Gets the keys of the document object as an ordered list to show in the result card. '''
        keys = super().result_card_keys()
        okeys = ['title']
        for key in keys:
            if key not in okeys:
                okeys.append(key)
        return okeys

    @classmethod
    def get_publications(cls, pmids, sources=[]):
        ''' Get publications from the list of PMIDs. '''
        if pmids is None or not pmids:
            return None
        from elastic.search import Search, ElasticQuery
        pubs = Search(ElasticQuery(Query.ids(pmids), sources=sources),
                      idx=ElasticSettings.idx('PUBLICATION', 'PUBLICATION'), size=2).search().docs
        return pubs

    @classmethod
    def get_pub_docs_by_pmid(cls, pmids, sources=None):
        ''' Get the publication documents for a list of PMIDs.
        A dictionary is returned with the key being the PMID and the
        value the publication document. '''
        pubs = {}

        def get_pubs(resp_json):
            hits = resp_json['hits']['hits']
            for hit in hits:
                pubs[hit['_id']] = PublicationDocument(hit)
        from elastic.search import ElasticQuery, ScanAndScroll
        query = ElasticQuery(Query.ids(pmids), sources=sources)
        ScanAndScroll.scan_and_scroll(ElasticSettings.idx('PUBLICATION'), call_fun=get_pubs, query=query)
        return pubs
