''' Gene page tests. '''
import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from pydgin.tests.data.settings_idx import PydginTestSettings
from pydgin.tests.tests_pydgin import PydginTestUtils


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def setUpModule():
    ''' create elastic indices for querying '''
    PydginTestSettings.setupIdx(['GENE_INTERACTIONS', 'GENE', 'GENE_PATHWAY', 'DISEASE', 'PUBLICATION',
                                 'GENE_CRITERIA_IS_GENE_IN_MHC', 'GENE_CRITERIA_CAND_GENE_IN_STUDY',
                                 'GENE_CRITERIA_GENE_IN_REGION', 'GENE_CRITERIA_CAND_GENE_IN_REGION'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    PydginTestSettings.tearDownIdx(['GENE', 'DISEASE', 'PUBLICATION',
                                    'GENE_CRITERIA_IS_GENE_IN_MHC', 'GENE_CRITERIA_CAND_GENE_IN_STUDY',
                                    'GENE_CRITERIA_GENE_IN_REGION', 'GENE_CRITERIA_CAND_GENE_IN_REGION'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class GenePageTest(TestCase):

    def test_url(self):
        ''' Test the gene page 404. '''
        url = reverse('gene_page_params')
        self.assertEqual(url, '/gene/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url2(self):
        ''' Test the gene page 404. '''
        url = reverse('gene_page_params')
        resp = self.client.get(url, {'g': 'ABC'})
        self.assertEqual(resp.status_code, 404)

    def test_js_test_page(self):
        ''' Test the JS test page. '''
        url = reverse('gene_js_test')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_url_ens_id(self):
        ''' Test the gene page. '''
        url = reverse('gene_page_params')
        resp = self.client.get(url, {'g': 'ENSG00000134242'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'PTPN22', resp.content)
        self.assertIn(b'protein_coding', resp.content)
        self.assertIn(b'LYP', resp.content)
        self.assertIn(b'26191', resp.content)
        self.assertContains(resp, '<title>PTPN22</title>')

    def test_hyperlinks(self):
        ''' Test example hyperlinks. '''
        PydginTestUtils.test_links_in_page(self, reverse('gene_page_params'), {'g': 'ENSG00000134242'})

    def test_pub_details(self):
        ''' Test the pub details JSON response. '''
        url = reverse('pub_details')
        json_resp = self.client.post(url, {'pmids[]': '24773525'})

        pmids = json.loads(json_resp.content.decode("utf-8"))['hits']
        self.assertEquals(len(pmids), 1)
        self.assertEquals(pmids[0]['_source']['pmid'], '24773525')

    def tests_interaction_details(self):
        ''' Test that interactors are retrieved. '''
        url = reverse('interaction_details')
        json_resp = self.client.post(url, {'ens_id': 'ENSG00000134242'})

        ints = json.loads(json_resp.content.decode("utf-8"))['hits']
        self.assertEquals(len(ints), 1)
        self.assertGreater(len(ints[0]['_source']['interactors']), 1)
        self.assertTrue('symbol' in ints[0]['_source']['interactors'][0])
        self.assertTrue('interactor' in ints[0]['_source']['interactors'][0])

    def test_genesets_details(self):
        ''' Test the pathway gene sets response. '''
        url = reverse('genesets')
        json_resp = self.client.post(url, {'ens_id': 'ENSG00000183709'})

        genes = json.loads(json_resp.content.decode("utf-8"))['hits']
        self.assertGreaterEqual(len(genes), 1)
        self.assertGreater(len(genes[0]['_source']['gene_sets']), 1)

    def test_gene_criteria_details(self):
        url = '/gene/criteria/'
        json_resp = self.client.post(url, {'feature_id': 'ENSG00000134242'})

        genecriteria = json.loads(json_resp.content.decode("utf-8"))['hits']
        types = [criteria['_type'] for criteria in genecriteria]
        self.assertGreaterEqual(len(types), 3)

        self.assertIn('cand_gene_in_study', types, 'cand_gene_in_study in types')
        self.assertIn('gene_in_region', types, 'cand_gene_in_study in types')
        self.assertIn('cand_gene_in_region', types, 'cand_gene_in_study in types')
