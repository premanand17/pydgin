''' Pydgin core application tests. '''
from django.test import TestCase
from django.test.utils import override_settings

from core.document import PydginDocument, FeatureDocument
from disease.document import DiseaseDocument
from elastic.aggs import Agg, Aggs
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query
from elastic.search import ElasticQuery, Search
from pydgin.tests.data.settings_idx import PydginTestSettings


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def setUpModule():
    ''' create elastic indices for querying '''
    PydginTestSettings.setupIdx(['GENE', 'DISEASE', 'PUBLICATION'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    PydginTestSettings.tearDownIdx(['GENE', 'DISEASE', 'PUBLICATION'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class PydginDocumentTest(TestCase):

    def test_doc(self):
        ''' Test return correct type of FeatureDocument. '''
        from gene.document import GeneDocument
        idx = PydginTestSettings.IDX['GENE']['indexName']
        idx_type = PydginTestSettings.IDX['GENE']['indexType']
        res = Search(search_query=ElasticQuery(Query.match_all(), sources=['symbol']),
                     idx=idx, idx_type=idx_type, size=2).search()
        for doc in res.docs:
            self.assertTrue(isinstance(doc, GeneDocument))

    def test_doc2(self):
        ''' Test return correct type of FeatureDocument using multiple index search. '''
        from gene.document import GeneDocument
        idx = PydginTestSettings.IDX['GENE']['indexName'] + ',' + PydginTestSettings.IDX['DISEASE']['indexName']
        res = Search(search_query=ElasticQuery(Query.match_all(), sources=['symbol', 'code']),
                     idx=idx, size=40).search()
        for doc in res.docs:
            self.assertTrue(isinstance(doc, GeneDocument) or isinstance(doc, DiseaseDocument))
            if isinstance(doc, DiseaseDocument):
                self.assertTrue(hasattr(doc, 'code'))

    def test_doc3(self):
        ''' Test return correct type of PydginDocument/FeatureDocument using multiple index search. '''
        idx = PydginTestSettings.IDX['DISEASE']['indexName'] + ',' + PydginTestSettings.IDX['PUBLICATION']['indexName']
        res = Search(search_query=ElasticQuery(Query.match_all(), sources=['code', 'pmid']),
                     idx=idx, size=40).search()

        for doc in res.docs:
            self.assertTrue(isinstance(doc, PydginDocument) or isinstance(doc, DiseaseDocument))
            if isinstance(doc, PydginDocument):
                self.assertTrue(hasattr(doc, 'pmid'))
            else:
                self.assertTrue(hasattr(doc, 'code'))

    def test_top_hits_sub_aggs(self):
        ''' Test a sub-aggregation of top hits return a PydginDocument/FeatureDocument. '''
        from gene.document import GeneDocument
        idx1 = PydginTestSettings.IDX['GENE']['indexName']
        idx2 = PydginTestSettings.IDX['PUBLICATION']['indexName']
        idx = idx1 + ',' + idx2
        sub_agg = Agg('idx_top_hits', 'top_hits', {"size": 55, "_source": ['symbol']})
        aggs = Aggs([Agg("idxs", "terms", {"field": "_index"}, sub_agg=sub_agg)])

        res = Search(aggs=aggs, idx=idx, size=0).search()
        top_hits = res.aggs['idxs'].get_docs_in_buckets(obj_document=ElasticSettings.get_document_factory())

        for doc in top_hits[idx1]['docs']:
            self.assertTrue(isinstance(doc, GeneDocument))
            self.assertTrue(isinstance(doc, FeatureDocument))
        for doc in top_hits[idx2]['docs']:
            self.assertTrue(isinstance(doc, PydginDocument))
