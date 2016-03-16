''' Gene page tests. '''
import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from pydgin.tests.data.settings_idx import PydginTestSettings
from pydgin.tests.tests_pydgin import PydginTestUtils


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def setUpModule():
    ''' Load test indices (study) '''
    PydginTestSettings.setupIdx(['STUDY', 'DISEASE', 'GENE', 'STUDY_HITS', 'PUBLICATION'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    PydginTestSettings.tearDownIdx(['STUDY', 'DISEASE', 'GENE', 'STUDY_HITS', 'PUBLICATION'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class StudyPageTest(TestCase):

    def test_url(self):
        ''' Test the region page 404. '''
        url = reverse('study_page_params')
        self.assertEqual(url, '/study/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url2(self):
        ''' Test the study page 404. '''
        url = reverse('study_page_params')
        resp = self.client.get(url, {'s': 'ABC'})
        self.assertEqual(resp.status_code, 404)

    def test_url_region_id(self):
        ''' Test the study page. '''
        url = reverse('study_page_params')
        resp = self.client.get(url, {'s': 'GDXHsS00004'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'GDXHsS00004', resp.content)
        self.assertContains(resp,
                            '<title>Whole Genome Association Study:T1D:Barrett JC:Nat Genet:2009:19430480</title>')

    def test_hyperlinks(self):
        ''' Test example hyperlinks. '''
        PydginTestUtils.test_links_in_page(self, reverse('study_page_params'), data={'s': 'GDXHsS00004'})


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class StudySectionTest(TestCase):

    def test_gene_study_section(self):
        ''' Test retrieving study information for the gene page view. '''
        url = reverse('study_section')
        json_resp = self.client.post(url, {'ens_id': 'ENSG00000134242'})
        studies = json.loads(json_resp.content.decode("utf-8"))['hits']
        self.assertGreaterEqual(len(studies), 10)
        self.assertTrue('dil_study_id' in studies[0]["_source"])

    def test_marker_study_section(self):
        ''' Test retrieving study information for the marker page view. '''
        url = reverse('study_section')
        json_resp = self.client.post(url, {'marker': 'rs2476601'})
        studies = json.loads(json_resp.content.decode("utf-8"))['hits']
        self.assertGreaterEqual(len(studies), 10)
        self.assertTrue('dil_study_id' in studies[0]["_source"])
