''' Pydgin Search Engine tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from elastic.search import Search, ElasticQuery, Update
from elastic.query import Query
from pydgin.tests.tests_pydgin import PydginTestUtils
from pydgin.tests.data.settings_idx import PydginTestSettings
import json


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def setUpModule():
    ''' create elastic indices for querying '''
    PydginTestSettings.setupIdx(['GENE', 'STUDY_HITS', 'PUBLICATION', 'DISEASE', 'MARKER', 'STUDY'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    PydginTestSettings.tearDownIdx(['GENE', 'STUDY_HITS', 'PUBLICATION', 'DISEASE', 'MARKER', 'STUDY'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class AuthSearchEngineTest(TestCase):

    def test_doc_auth(self):
        ''' Test private documents are not returned in the search. '''
        idx = PydginTestSettings.IDX['MARKER']['indexName']
        docs = Search(ElasticQuery(Query.match_all(), sources=['id']), idx=idx, size=1).search().docs
        self.assertEquals(len(docs), 1, "MARKER document")
        marker_id = getattr(docs[0], 'id')

        url = reverse('search_page')
        resp = self.client.post(url+'?idx=ALL&query='+marker_id)
        nhits1 = resp.context['hits_total']
        self.assertGreater(nhits1, 0, 'search hits > 0')
        # update document to be in DIL
        update_field = {"doc": {"group_name": "DIL"}}
        Update.update_doc(docs[0], update_field)
        Search.index_refresh(PydginTestSettings.IDX['MARKER']['indexName'])

        resp = self.client.post(url+'?idx=ALL&query='+marker_id)
        nhits2 = resp.context['hits_total']
        self.assertEqual(nhits1-1, nhits2, 'private document hidden')


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class SearchEngineTest(TestCase):

    def test_search_page(self):
        ''' Test the search page. '''
        url = reverse('advanced_search_page')
        self.assertEqual(url, '/search/advanced')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'search_engine/advanced_search.html')

    def test_search(self):
        ''' Test the search. '''
        url = reverse('search_page')
        resp = self.client.post(url+'?idx=ALL&query=%2BPTPN22+%2Btodd')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['query'], "+PTPN22 +todd")
        self.assertGreater(resp.context['hits_total'], 0)
        self.assertTemplateUsed(resp, 'search_engine/result.html')

    def test_search2(self):
        ''' Test the search on specified fields in the index. '''
        url = reverse('search_page')
        resp = self.client.post(url+'?idx=ALL&query=%2jouhn+%2Btodd+%2Bt1d',
                                {"publication_tags_disease": "publication:tags:disease",
                                 "publication_authors_name": "publication:authors:name"})
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.context['hits_total'], 0)

    def test_search3(self):
        ''' Test the search specifying the field in the query. '''
        url = reverse('search_page')
        resp = self.client.get(url+'?idx=ALL&query=dbxrefs.swissprot:Q9Y2R2')
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.context['hits_total'], 0)

    def test_search_filters(self):
        ''' Test the search with filters applied. '''
        url = "%s?idx=GENE&query=PTPN2*" % reverse('search_page')
        resp = self.client.post(url, data={"biotypes": "protein_coding", "saved-biotypes": "antisense",
                                           "saved-biotypes": "antisense"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['query'], "PTPN2*")
        self.assertGreaterEqual(resp.context['hits_total'], 1)
        self.assertTemplateUsed(resp, 'search_engine/result.html')
        biotypes = resp.context['aggs']['biotypes'].get_buckets()
        self.assertEqual(len(biotypes), 2)
        if biotypes[0]['key'] == 'protein_coding':
            protein_coding = biotypes[0]
            antisense = biotypes[1]
        else:
            protein_coding = biotypes[1]
            antisense = biotypes[0]
        self.assertGreater(protein_coding['doc_count'], 0)
        self.assertEquals(antisense['doc_count'], 0)

    def test_search_filters2(self):
        ''' Test applying categories filter. Query first without filter and then
        with to get just the gene. '''
        url = "%s?idx=ALL&query=PTPN12" % reverse('search_page')
        data = {
            'categories': 'gene',
            'categories': 'publication',
            'biotypes': 'protein_coding',
            'gene_symbol': 'gene:symbol',
            'publication_title': 'publication:title'
        }
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 200)
        nhits1 = resp.context['hits_total']
        self.assertGreater(nhits1, 1)

        del data['publication_title']
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 200)
        nhits2 = resp.context['hits_total']
        self.assertEqual(nhits2, 1)
        self.assertGreater(nhits1, nhits2)

    def test_search_filters3(self):
        ''' Test filtering the gene biotype as well as other index types. '''
        url = reverse('search_page')
        resp = self.client.get(url, {"idx": "ALL", "query": "PTPN12",
                                     "categories": "gene", "categories": "publication",
                                     "biotypes": "protein_coding"})
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.context['hits_total'], 1)

    def test_suggester(self):
        ''' Test the auto suggester for searches. '''
        url = reverse('suggester')
        resp = self.client.get(url, {"idx": "ALL", "term": "PT"})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf-8'))
        self.assertTrue('PTPN22' in data['data'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class HyperLinksTest(TestCase):
    ''' Hyperlinks on live site. '''

    def test_hyperlinks(self):
        ''' Test example hyperlinks. '''
        PydginTestUtils.test_links_in_page(self, reverse('search_page'))
