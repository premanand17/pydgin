''' Pydgin Search Engine tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse
import json
from pydgin.tests.tests_pydgin import PydginTestUtils
from pydgin_auth.elastic_model_factory import ElasticPermissionModelFactory


class SearchEngineTest(TestCase):

    def setUp(self):
        # create elastic models
        ElasticPermissionModelFactory.create_dynamic_models()

    def test_search_page(self):
        ''' Test the search page. '''
        url = reverse('search_page')
        self.assertEqual(url, '/search/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'search_engine/search.html')

    def test_hyperlinks(self):
        ''' Test example hyperlinks. '''
        PydginTestUtils.test_links_in_page(self, reverse('search_page'))

    def test_search(self):
        ''' Test the search. '''
        url = reverse('search_page')
        resp = self.client.get(url, {"idx": "ALL", "query": "+PTPN22 +todd"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['query'], "+PTPN22 +todd")
        self.assertGreater(resp.context['hits_total'], 0)
        self.assertTemplateUsed(resp, 'search_engine/result.html')

    def test_search2(self):
        ''' Test the search on specified fields in the index. '''
        url = reverse('search_page')
        resp = self.client.get(url, {"idx": "ALL", "query": '+john +todd +t1d',
                                     "publication_tags_disease": "publication:tags:disease",
                                     "publication_authors_name": "publication:authors:name"})
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.context['hits_total'], 0)

    def test_search3(self):
        ''' Test the search specifying the field in the query. '''
        url = reverse('search_page')
        resp = self.client.get(url, {"idx": "ALL", "query": 'dbxrefs.swissprot:Q9Y2R2'})
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.context['hits_total'], 0)

    def test_search_filters(self):
        ''' Test the search with filters applied. '''
        url = "%s?idx=ALL&query=PTPN2*" % reverse('search_page')
        resp = self.client.post(url, data={"biotypes": "protein_coding"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['query'], "PTPN2*")
        self.assertGreaterEqual(resp.context['hits_total'], 1)
        self.assertTemplateUsed(resp, 'search_engine/result.html')
        biotypes = resp.context['aggs']['biotypes'].get_buckets()
        self.assertEqual(len(biotypes), 1)
        self.assertEqual(biotypes[0]['key'], 'protein_coding')

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
