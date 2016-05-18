''' Data integrity tests for disease index '''
from django.test import TestCase
from elastic.elastic_settings import ElasticSettings
import logging
from django.test.utils import override_settings
from pydgin.tests.data.settings_idx import PydginTestSettings

logger = logging.getLogger(__name__)


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class DiseaseTest(TestCase):
    idx = ''

    @classmethod
    def setUp(cls):
        DiseaseTest.idx = ElasticSettings.idx('DISEASE')
        PydginTestSettings.setupIdx(['DISEASE'])

    @classmethod
    def tearDown(cls):
        PydginTestSettings.tearDownIdx(['DISEASE'])

    def test_all_diseases(self):
        ''' Test getting all diseases on the site '''
        from disease.utils import Disease
        (main, other) = Disease.get_site_diseases()
        self.assertEqual(12, len(main), "12 main diseases found when searching for all diseases")
        self.assertEqual(7, len(other), "7 other diseases found when searching for all diseases")

    def test_main_diseases(self):
        ''' Test getting all diseases on the site '''
        from disease.utils import Disease
        (main, other) = Disease.get_site_diseases(tier=0)
        self.assertEqual(12, len(main), "12 main diseases found when searching for main diseases")
        self.assertEqual(0, len(other), "0 other diseases found when searching for main diseases")

    def test_other_diseases(self):
        ''' Test getting all diseases on the site '''
        from disease.utils import Disease
        (main, other) = Disease.get_site_diseases(tier=1)
        self.assertEqual(0, len(main), "12 main diseases found when searching for other diseases")
        self.assertEqual(7, len(other), "7 other diseases found when searching for other diseases")

    def test_site_disease_codes(self):
        ''' Test getting all diseases on the site '''
        from disease.utils import Disease
        (main, other) = Disease.get_site_disease_codes()
        self.assertEqual(12, len(main), "12 main diseases found ")
        self.assertEqual(7, len(other), "7 other diseases found when searching for other diseases")
