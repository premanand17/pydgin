''' Marker page tests. '''
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from pydgin.tests.data.settings_idx import PydginTestSettings
import json


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def setUpModule():
    ''' Load test indices (marker) '''
    PydginTestSettings.setupIdx(['MARKER', 'MARKER_IC', 'DISEASE',
                                 'MARKER_CRITERIA_IS_MARKER_IN_MHC', 'MARKER_CRITERIA_IS_AN_INDEX_SNP',
                                 'MARKER_CRITERIA_MARKER_IS_GWAS_SIGNIFICANT_STUDY',
                                 'MARKER_CRITERIA_RSQ_WITH_INDEX_SNP'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    PydginTestSettings.tearDownIdx(['MARKER', 'DISEASE',
                                    'MARKER_CRITERIA_IS_MARKER_IN_MHC', 'MARKER_CRITERIA_IS_AN_INDEX_SNP',
                                    'MARKER_CRITERIA_MARKER_IS_GWAS_SIGNIFICANT_STUDY',
                                    'MARKER_CRITERIA_RSQ_WITH_INDEX_SNP'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class MarkerPageTest(TestCase):

    def test_url(self):
        ''' Test the marker page 404. '''
        url = reverse('marker_page_params')
        self.assertEqual(url, '/marker/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url2(self):
        ''' Test the marker page 404. '''
        url = reverse('marker_page_params')
        resp = self.client.get(url, {'m': 'ABC'})
        self.assertEqual(resp.status_code, 404)

    def test_url_rs_id(self):
        ''' Test the marker page. '''
        url = reverse('marker_page_params')
        resp = self.client.get(url, {'m': 'rs2476601'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'rs2476601', resp.content)
        self.assertIn(b'imm_1_114179091', resp.content)

    def test_marker_criteria_details(self):
        ''' Test the criteria section. '''
        url = '/marker/criteria/'
        json_resp = self.client.post(url, {'feature_id': 'rs2476601'})

        markercriteria = json.loads(json_resp.content.decode("utf-8"))['hits']
        types = [criteria['_type'] for criteria in markercriteria]
        self.assertGreaterEqual(len(types), 3)

        self.assertIn('is_an_index_snp', types, 'is_an_index_snp in types')
        self.assertIn('marker_is_gwas_significant_in_study', types, 'marker_is_gwas_significant_in_study in types')
        self.assertIn('rsq_with_index_snp', types, 'rsq_with_index_snp in types')
