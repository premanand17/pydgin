''' Settings used for the test indices. '''
import json
import os
import requests

from django.core.management import call_command

from elastic.elastic_settings import ElasticSettings
from elastic.search import Search


class PydginTestSettings(object):
    SEARCH_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    SEARCH_TEST_DATA_PATH = os.path.join(SEARCH_BASE_DIR, 'data/')
    SEARCH_SUFFIX = ElasticSettings.getattr('TEST') + '__pydgin'
    if SEARCH_SUFFIX is None:
        SEARCH_SUFFIX = "test"

    NUMBER_OF_SHARDS = 1

    IDX = {
        'GENE': {
            'indexName': 'test__gene_'+SEARCH_SUFFIX,
            'indexType': 'gene',
            'indexJson': SEARCH_TEST_DATA_PATH+'gene.json'
        },
        'GENE_INTERACTIONS': {
            'indexName': 'test__gene_'+SEARCH_SUFFIX,
            'indexType': 'gene_interactions_test',
            'indexJson': SEARCH_TEST_DATA_PATH+'gene_interactions.json'
        },
        'GENE_PATHWAY': {
            'indexName': 'test__gene_'+SEARCH_SUFFIX,
            'indexType': 'pathway_genesets',
            'indexJson': SEARCH_TEST_DATA_PATH+'gene_pathway.json'
        },
        'STUDY_HITS': {
            'indexName': 'test__region_'+SEARCH_SUFFIX,
            'indexType': 'study_test',
            'indexJson': SEARCH_TEST_DATA_PATH+'study_hits.json'
        },
        'REGION': {
            'indexName': 'test__region_'+SEARCH_SUFFIX,
            'indexType': 'region_test',
            'indexJson': SEARCH_TEST_DATA_PATH+'region.json'
        },
        'STUDY': {
            'indexName': 'test__study_'+SEARCH_SUFFIX,
            'indexType': 'study_test',
            'indexJson': SEARCH_TEST_DATA_PATH+'study.json'
        },
        'DISEASE_LOCUS': {
            'indexName': 'test__region_'+SEARCH_SUFFIX,
            'indexType': 'disease_locus_test',
            'indexJson': SEARCH_TEST_DATA_PATH+'disease_locus.json'
        },
        'PUBLICATION': {
            'indexName': 'test__pub_'+SEARCH_SUFFIX,
            'indexType': 'publication_test',
            'indexJson': SEARCH_TEST_DATA_PATH+'pub.json'
        },
        'DISEASE': {
            'indexName': 'test__disease_'+SEARCH_SUFFIX,
            'indexType': 'disease_test',
            'indexJson': SEARCH_TEST_DATA_PATH+'disease.json'
        },
        'MARKER': {
            'indexName': 'test__marker_'+SEARCH_SUFFIX,
            'indexType': 'marker',
            'indexJson': SEARCH_TEST_DATA_PATH+'marker.json'
        },
        'MARKER_IC': {
            'indexName': 'test__marker_'+SEARCH_SUFFIX,
            'indexType': 'immunochip',
            'indexJson': SEARCH_TEST_DATA_PATH+'marker_ic.json'
        },
        'IC_STATS': {
            'indexName': 'test__ic_stats_'+SEARCH_SUFFIX,
            'indexType': 't1d_onengut',
            'indexJson': SEARCH_TEST_DATA_PATH+'ic_stats.json'
        },
        'GENE_CRITERIA': {
            'indexName': 'test__gene_criteria_'+SEARCH_SUFFIX,
        },
        'GENE_CRITERIA_IS_GENE_IN_MHC': {
            'indexName': 'test__gene_criteria_'+SEARCH_SUFFIX,
            'indexType': 'is_gene_in_mhc',
            'indexJson': SEARCH_TEST_DATA_PATH+'/criteria/gene_criteria_is_in_mhc.json'
        },
        'GENE_CRITERIA_CAND_GENE_IN_STUDY': {
            'indexName': 'test__gene_criteria_'+SEARCH_SUFFIX,
            'indexType': 'cand_gene_in_study',
            'indexJson': SEARCH_TEST_DATA_PATH+'/criteria/gene_criteria_cand_gene_in_study.json'
        },
        'GENE_CRITERIA_CAND_GENE_IN_REGION': {
            'indexName': 'test__gene_criteria_'+SEARCH_SUFFIX,
            'indexType': 'cand_gene_in_region',
            'indexJson': SEARCH_TEST_DATA_PATH+'/criteria/gene_criteria_cand_gene_in_region.json'
        },
        'GENE_CRITERIA_GENE_IN_REGION': {
            'indexName': 'test__gene_criteria_'+SEARCH_SUFFIX,
            'indexType': 'gene_in_region',
            'indexJson': SEARCH_TEST_DATA_PATH+'/criteria/gene_criteria_gene_in_region.json'
        },
        'MARKER_CRITERIA': {
            'indexName': 'test__marker_criteria_'+SEARCH_SUFFIX,
        },
        'MARKER_CRITERIA_IS_MARKER_IN_MHC': {
            'indexName': 'test__marker_criteria_'+SEARCH_SUFFIX,
            'indexType': 'is_marker_in_mhc',
            'indexJson': SEARCH_TEST_DATA_PATH+'/criteria/marker_criteria_is_marker_in_mhc.json'
        },
        'MARKER_CRITERIA_IS_AN_INDEX_SNP': {
            'indexName': 'test__marker_criteria_'+SEARCH_SUFFIX,
            'indexType': 'is_an_index_snp',
            'indexJson': SEARCH_TEST_DATA_PATH+'/criteria/marker_criteria_is_an_index_snp.json'
        },
        'MARKER_CRITERIA_MARKER_IS_GWAS_SIGNIFICANT_STUDY': {
            'indexName': 'test__marker_criteria_'+SEARCH_SUFFIX,
            'indexType': 'marker_is_gwas_significant_in_study',
            'indexJson': SEARCH_TEST_DATA_PATH+'/criteria/marker_criteria_is_gwas_significant_in_study.json'
        },
        'MARKER_CRITERIA_RSQ_WITH_INDEX_SNP': {
            'indexName': 'test__marker_criteria_'+SEARCH_SUFFIX,
            'indexType': 'rsq_with_index_snp',
            'indexJson': SEARCH_TEST_DATA_PATH+'/criteria/marker_criteria_rsq_with_index_snp.json'
        },
        'REGION_CRITERIA': {
            'indexName': 'test__region_criteria_'+SEARCH_SUFFIX,
        },
        'REGION_CRITERIA_IS_REGION_IN_MHC': {
            'indexName': 'test__region_criteria_'+SEARCH_SUFFIX,
            'indexType': 'is_region_in_mhc',
            'indexJson': SEARCH_TEST_DATA_PATH+'/criteria/region_criteria_is_region_in_mhc.json'
        },
        'REGION_CRITERIA_IS_REGION_FOR_DISEASE': {
            'indexName': 'test__region_criteria_'+SEARCH_SUFFIX,
            'indexType': 'is_region_for_disease',
            'indexJson': SEARCH_TEST_DATA_PATH+'/criteria/region_criteria_is_region_for_disease.json'
        },
        'STUDY_CRITERIA': {
            'indexName': 'test__study_criteria_'+SEARCH_SUFFIX,
        },
        'STUDY_CRITERIA_STUDY_FOR_DISEASE': {
            'indexName': 'test__study_criteria_'+SEARCH_SUFFIX,
            'indexType': 'study_for_disease',
            'indexJson': SEARCH_TEST_DATA_PATH+'/criteria/study_criteria_study_for_disease.json'
        },
    }

    OVERRIDE_SETTINGS = {
        'default': {
            'ELASTIC_URL': [ElasticSettings.url()],
            'DOCUMENT_FACTORY': 'core.document.PydginDocument',
            'IDX': {
                'GENE': {
                    'name': IDX['GENE']['indexName'],
                    'idx_type': {
                        'GENE': {'type': IDX['GENE']['indexType'], 'search': True,
                                 'auth_public': True, 'class': 'gene.document.GeneDocument'},
                        'PATHWAY': {'type': 'pathway_genesets', 'auth_public': True},
                        'INTERACTIONS': {'type': IDX['GENE_INTERACTIONS']['indexType'],  'auth_public': True}
                    },
                    'suggester': True, 'auth_public': True
                },
                'PUBLICATION': {
                    'name': IDX['PUBLICATION']['indexName'],
                    'idx_type': {
                        'PUBLICATION': {'type': IDX['PUBLICATION']['indexType'], 'search': True,
                                        'auth_public': True, 'class': 'core.document.PublicationDocument'}
                    },
                    'suggester': True, 'auth_public': True
                },
                'DISEASE': {
                    'name': IDX['DISEASE']['indexName'],
                    'idx_type': {
                        'DISEASE': {'type': IDX['DISEASE']['indexType'], 'search': True,
                                    'auth_public': True, 'class': 'disease.document.DiseaseDocument'}
                    },
                    'suggester': True, 'auth_public': True
                },
                'MARKER': {
                    'name': IDX['MARKER']['indexName'], 'build': 38,
                    'idx_type': {
                        'MARKER': {'type': IDX['MARKER']['indexType'], 'search': True,
                                   'auth_public': True, 'class': 'marker.document.MarkerDocument'},
                        'IC': {'type': IDX['MARKER_IC']['indexType'], 'search': True,
                               'auth_public': True, 'class': 'marker.document.ImmunoChipDocument'}
                    },
                    'suggester': True,
                    'auth_public': True
                },
                'IC_STATS': {
                   'name': IDX['IC_STATS']['indexName'],
                   'idx_type': {
                       'T1D_ONENGUT': {'type': IDX['IC_STATS']['indexType'], 'auth_public': True}
                   },
                   'auth_public': True
                },
                'REGION': {
                   'name': IDX['STUDY_HITS']['indexName'],
                   'idx_type': {
                        'STUDY_HITS': {'type': IDX['STUDY_HITS']['indexType'], 'search': True,
                                       'auth_public': True, 'class': 'region.document.StudyHitDocument'},
                        'DISEASE_LOCUS': {'type': IDX['DISEASE_LOCUS']['indexType'],
                                          'auth_public': True, 'class': 'region.document.DiseaseLocusDocument'},
                        'REGION': {'type': IDX['REGION']['indexType'], 'search': True,
                                   'auth_public': True, 'class': 'region.document.RegionDocument'}
                    },
                   'auth_public': True
                },
                'STUDY': {
                    'name': IDX['STUDY']['indexName'],
                    'idx_type': {
                        'STUDY': {'type': IDX['STUDY']['indexType'], 'auth_public': True,
                                  'class': 'study.document.StudyDocument', 'search': True}
                    },
                    'suggester': True,
                    'auth_public': True
                },
                'GENE_CRITERIA': {
                    'name': IDX['GENE_CRITERIA']['indexName'],
                    'idx_type': {
                        'IS_GENE_IN_MHC': {'type': IDX['GENE_CRITERIA_IS_GENE_IN_MHC']['indexType'],
                                           'auth_public': True},
                        'CAND_GENE_IN_STUDY': {'type': IDX['GENE_CRITERIA_CAND_GENE_IN_STUDY']['indexType'],
                                               'auth_public': True},
                        'CAND_GENE_IN_REGION': {'type': IDX['GENE_CRITERIA_CAND_GENE_IN_REGION']['indexType'],
                                                'auth_public': True},
                        'GENE_IN_REGION': {'type': IDX['GENE_CRITERIA_GENE_IN_REGION']['indexType'],
                                           'auth_public': True},
                                 },
                    'auth_public': True
                },
                'MARKER_CRITERIA': {
                    'name': IDX['MARKER_CRITERIA']['indexName'],
                    'idx_type': {
                        'IS_MARKER_IN_MHC': {'type': IDX['MARKER_CRITERIA_IS_MARKER_IN_MHC']['indexType'],
                                             'auth_public': True},
                        'IS_AN_INDEX_SNP': {'type': IDX['MARKER_CRITERIA_IS_AN_INDEX_SNP']['indexType'],
                                            'auth_public': True},
                        'MARKER_IS_GWAS_SIGNIFICANT_STUDY': {'type': IDX['MARKER_CRITERIA_MARKER_IS_GWAS_SIGNIFICANT_STUDY']['indexType'],  # @IgnorePep8
                                                             'auth_public': True},
                        'RSQ_WITH_INDEX_SNP': {'type': IDX['MARKER_CRITERIA_RSQ_WITH_INDEX_SNP']['indexType'],
                                               'auth_public': True},
                            },
                    'auth_public': True
                    },
                'REGION_CRITERIA': {
                    'name': IDX['REGION_CRITERIA']['indexName'],
                    'idx_type': {
                        'IS_REGION_IN_MHC': {'type': IDX['REGION_CRITERIA_IS_REGION_IN_MHC']['indexType'],
                                             'auth_public': True},
                        'IS_REGION_FOR_DISEASE': {'type': IDX['REGION_CRITERIA_IS_REGION_FOR_DISEASE']['indexType'],
                                                  'auth_public': True},

                            },
                    'auth_public': True
                    },
                'STUDY_CRITERIA': {
                    'name': IDX['STUDY_CRITERIA']['indexName'],
                    'idx_type': {
                        'STUDY_FOR_DISEASE': {'type': IDX['STUDY_CRITERIA_STUDY_FOR_DISEASE']['indexType'],
                                              'auth_public': True},
                        },
                    'auth_public': True
                    },
            }
        }
    }

    @classmethod
    def setupIdx(cls, idx_name_arr):
        ''' Setup indices in the given array of key names (e.g. ['GENE', 'DIISEASE', ...]). '''
        idx_settings = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "full_name": {"filter": ["standard", "lowercase"], "tokenizer": "keyword"}}
                },
                "number_of_shards": PydginTestSettings.NUMBER_OF_SHARDS
            }
        }
        IDX = PydginTestSettings.IDX
        for name in idx_name_arr:
            requests.put(ElasticSettings.url() + '/' + IDX[name]['indexName'], data=json.dumps(idx_settings))
            call_command('index_search', **IDX[name])
        for name in idx_name_arr:
            # wait for the elastic load to finish
            Search.index_refresh(IDX[name]['indexName'])

    @classmethod
    def tearDownIdx(cls, idx_name_arr):
        ''' Remove indices by their key names (e.g. ['GENE', 'DIISEASE', ...]). '''
        for name in idx_name_arr:
            requests.delete(ElasticSettings.url() + '/' + PydginTestSettings.IDX[name]['indexName'])
