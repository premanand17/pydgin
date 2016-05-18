''' Test for feature locations rest interface. '''
import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings
from pydgin.tests.data.settings_idx import PydginTestSettings


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def setUpModule():
    ''' create elastic indices for querying '''
    PydginTestSettings.setupIdx(['GENE', 'MARKER', 'STUDY_HITS', 'DISEASE_LOCUS', 'REGION', 'DISEASE'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    PydginTestSettings.tearDownIdx(['GENE', 'MARKER', 'STUDY_HITS', 'DISEASE_LOCUS', 'REGION', 'DISEASE'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class LocationsRestTest(TestCase):

    def test_locations_list(self):
        ''' Test retrieving locations for gene, marker and regions. '''
        url = reverse('rest:locations-list')
        response = self.client.get(url, data={'feature': 'rs2476601', 'build': 'hg38'})
        loc = json.loads(response.content.decode("utf-8"))[0]
        self.assertGreater(len(loc), 0, 'results found')

        response = self.client.get(url, data={'feature': 'PTPN22', 'build': 'hg38'})
        loc = json.loads(response.content.decode("utf-8"))[0]
        self.assertGreater(len(loc), 0, 'results found')

        response = self.client.get(url, data={'feature': '1p13.2', 'build': 'hg38'})
        loc = json.loads(response.content.decode("utf-8"))[0]
        self.assertGreater(len(loc), 0, 'results found')
