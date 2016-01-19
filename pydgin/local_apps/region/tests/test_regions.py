''' Data integrity tests for region index '''
from django.test import TestCase
from elastic.elastic_settings import ElasticSettings
from data_pipeline.data_integrity.utils import DataIntegrityUtils
import logging
from elastic.query import RangeQuery, Query
from elastic.search import Search, ElasticQuery
from region import utils

logger = logging.getLogger(__name__)


class RegionTest(TestCase):
    '''Region test '''
    IDX_KEY = 'REGION'
    idx = ''
    idx_type = ''
    IDX_TYPE_KEYS = ['STUDY_HITS', 'DISEASE_LOCUS', 'REGION']

    @classmethod
    def setUpClass(cls):
        idx = ElasticSettings.idx(RegionTest.IDX_KEY, 'STUDY_HITS')
        (RegionTest.idx, RegionTest.idx_type) = idx.split('/')

    @classmethod
    def tearDownClass(cls):
        pass

    def test_hit2region(self):
        ''' Test region returned for hit id. '''
        docs = DataIntegrityUtils.get_rdm_docs(RegionTest.idx, RegionTest.idx_type,
                                               qbool=RangeQuery("tier", lte=2), sources=[], size=1)
        regions = utils.Region.hits_to_regions(docs)
        self.assertEquals(len(regions), 1)
        region_doc = regions[0]
        hit_doc = docs[0]
        self.assertEquals(getattr(hit_doc, "chr_band").lower(), getattr(region_doc, "region_name").lower())
        self.assertIn(getattr(hit_doc, "disease"), getattr(region_doc, "tags")['disease'],
                      getattr(hit_doc, "disease") + "exists in list of tagged diseases on parent region")

    def test_pad_region(self):
        ''' Test the padding of a region based on it's disease_loci & hits. '''
        idx = ElasticSettings.idx(RegionTest.IDX_KEY, 'REGION')
        (idx, idx_type) = idx.split('/')
        docs = DataIntegrityUtils.get_rdm_docs(idx, idx_type, qbool=Query.match_all(), sources=[], size=1)

        region = docs[0]
        self.assertFalse(getattr(region, "build_info"), "Region doesn't contain any positional details")
        self.assertFalse(getattr(region, "markers"), "Region doesn't contain any marker details")
        self.assertFalse(getattr(region, "hits"), "Region doesn't contain any HIT details")
        self.assertFalse(getattr(region, "genes"), "Region doesn't contain any gene details")
        self.assertFalse(getattr(region, "studies"), "Region doesn't contain any study details")
        self.assertFalse(getattr(region, "pmids"), "Region doesn't contain any publication details")

        newRegion = utils.Region.pad_region_doc(region)
        self.assertTrue(getattr(newRegion, "build_info"), "New region contains positional details")
        self.assertTrue(getattr(newRegion, "markers"), "New region contains marker details")
        self.assertGreaterEqual(len(getattr(newRegion, "markers")), 1, "Region contains at least 1 marker")
        self.assertTrue(getattr(newRegion, "hits"), "New region contains hit details")
        self.assertGreaterEqual(len(getattr(newRegion, "hits")), 1, "Region contains at least 1 HIT")

        if len(getattr(newRegion, "genes")) > 0:
            query = ElasticQuery(Query.ids(getattr(newRegion, "genes")))
            resultObject = Search(query, idx=ElasticSettings.idx('GENE', 'GENE'),
                                  size=len(getattr(newRegion, "genes"))).search()
            self.assertEqual(len(getattr(newRegion, "genes")), resultObject.hits_total,
                             "All genes on region found in GENE index")

        if len(getattr(newRegion, "studies")) > 0:
            query = ElasticQuery(Query.ids(getattr(newRegion, "studies")))
            resultObject = Search(query, idx=ElasticSettings.idx('STUDY', 'STUDY'),
                                  size=len(getattr(newRegion, "studies"))).search()
            self.assertEqual(len(getattr(newRegion, "studies")), resultObject.hits_total,
                             "All study ids for region found in STUDY index")

        if len(getattr(newRegion, "pmids")) > 0:
            query = ElasticQuery(Query.ids(getattr(newRegion, "pmids")))
            resultObject = Search(query, idx=ElasticSettings.idx('PUBLICATION', 'PUBLICATION'),
                                  size=len(getattr(newRegion, "pmids"))).search()
            self.assertEqual(len(getattr(newRegion, "pmids")), resultObject.hits_total,
                             "All PMIDs for region found in PUBLICATION index")
