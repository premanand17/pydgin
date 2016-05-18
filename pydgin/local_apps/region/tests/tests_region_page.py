''' Region page tests. '''
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from pydgin.tests.data.settings_idx import PydginTestSettings
from pydgin.tests.tests_pydgin import PydginTestUtils
import json


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def setUpModule():
    ''' Load test indices (region) '''
    PydginTestSettings.setupIdx(['REGION', 'STUDY_HITS', 'DISEASE',
                                 'REGION_CRITERIA_IS_REGION_IN_MHC', 'REGION_CRITERIA_IS_REGION_FOR_DISEASE'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    PydginTestSettings.tearDownIdx(['REGION', 'DISEASE',
                                    'REGION_CRITERIA_IS_REGION_IN_MHC', 'REGION_CRITERIA_IS_REGION_FOR_DISEASE'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class RegionPageTest(TestCase):

    def test_url(self):
        ''' Test the region page 404. '''
        url = reverse('region_page_params')
        self.assertEqual(url, '/region/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url2(self):
        ''' Test the region page 404. '''
        url = reverse('region_page_params')
        resp = self.client.get(url, {'r': 'ABC'})
        self.assertEqual(resp.status_code, 404)

    def test_url_region_id(self):
        ''' Test the region page. '''
        url = reverse('region_page_params')
        resp = self.client.get(url, {'r': '1p13.2_019'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'1p13.2', resp.content)
        self.assertContains(resp, '<title>1p13.2</title>')

    def test_hyperlinks(self):
        ''' Test example hyperlinks. '''
        PydginTestUtils.test_links_in_page(self, reverse('region_page_params'), data={'r': '1p13.2_019'})

    def test_region_criteria_details(self):
        ''' Test the criteria section. '''
        url = '/region/criteria/'
        json_resp = self.client.post(url, {'feature_id': '1p13.2_019'})

        regioncriteria = json.loads(json_resp.content.decode("utf-8"))['hits']
        types = [criteria['_type'] for criteria in regioncriteria]
        self.assertGreaterEqual(len(types), 1)

        self.assertIn('is_region_for_disease', types, 'is_region_for_disease in types')
