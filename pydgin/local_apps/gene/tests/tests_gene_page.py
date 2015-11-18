''' Gene page tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse
from pydgin.tests.tests_pydgin import PydginTestUtils
from gene import views
from django.http.request import HttpRequest
import json


class GenePageTest(TestCase):

    def test_url(self):
        ''' Test the gene page 404. '''
        url = reverse('gene_page')
        self.assertEqual(url, '/gene/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url2(self):
        ''' Test the gene page 404. '''
        url = reverse('gene_page')
        resp = self.client.get(url, {'g': 'ABC'})
        self.assertEqual(resp.status_code, 404)

    def test_url_ens_id(self):
        ''' Test the gene page. '''
        url = reverse('gene_page')
        resp = self.client.get(url, {'g': 'ENSG00000134242'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'PTPN22', resp.content)
        self.assertIn(b'protein_coding', resp.content)
        self.assertIn(b'LYP', resp.content)
        self.assertIn(b'26191', resp.content)
        self.assertContains(resp, '<title>ENSG00000134242</title>')

    def test_hyperlinks(self):
        ''' Test example hyperlinks. '''
        PydginTestUtils.test_links_in_page(self, reverse('gene_page'), data={'g': 'ENSG00000134242'})

    def test_pub_details(self):
        ''' Test the pub details JSON response. '''
        req = HttpRequest()
        req.POST['pmids[]'] = '19923204'
        json_resp = views.pub_details(req)
        pmids = json.loads(json_resp.content.decode("utf-8"))['hits']
        self.assertEquals(len(pmids), 1)
        self.assertEquals(pmids[0]['_source']['pmid'], '19923204')

    def tests_interaction_details(self):
        ''' Test that interactors are retrieved. '''
        req = HttpRequest()
        req.POST['ens_id'] = 'ENSG00000134242'
        json_resp = views.interaction_details(req)
        ints = json.loads(json_resp.content.decode("utf-8"))['hits']
        self.assertEquals(len(ints), 1)
        self.assertGreater(len(ints[0]['_source']['interactors']), 1)
        self.assertTrue('symbol' in ints[0]['_source']['interactors'][0])
        self.assertTrue('interactor' in ints[0]['_source']['interactors'][0])

    def test_genesets_details(self):
        ''' Test the pathway gene sets response. '''
        req = HttpRequest()
        req.POST['ens_id'] = 'ENSG00000183709'
        json_resp = views.genesets_details(req)
        genes = json.loads(json_resp.content.decode("utf-8"))['hits']
        self.assertGreaterEqual(len(genes), 1)
        self.assertGreater(len(genes[0]['_source']['gene_sets']), 1)

    def test_studies_details(self):
        ''' Test retrieving study information for the view. '''
        req = HttpRequest()
        req.POST['ens_id'] = 'ENSG00000134242'
        json_resp = views.studies_details(req)
        studies = json.loads(json_resp.content.decode("utf-8"))['hits']
        self.assertGreaterEqual(len(studies), 15)
        self.assertTrue('dil_study_id' in studies[0]["_source"])
