''' Utility functions for Diseases. '''

import logging
from elastic.elastic_settings import ElasticSettings
from elastic.search import Search, ElasticQuery, Sort
from elastic.query import Query

logger = logging.getLogger(__name__)


def diseases_cache():
    ''' Caching main (tier 0) and other (tier 1) diseases. '''
    def _cache_diseases(obj):
        res = Search(search_query=ElasticQuery(Query.match_all()),
                     idx=ElasticSettings.idx('DISEASE', 'DISEASE'),
                     qsort=Sort('code:asc')).search()
        for doc in res.docs:
            setattr(doc, 'code', getattr(doc, 'code').upper())

        setattr(obj, 'MAIN', [doc for doc in res.docs if getattr(doc, "tier") == 0])
        setattr(obj, 'OTHER', [doc for doc in res.docs if getattr(doc, "tier") == 1])
        return obj
    return _cache_diseases


@diseases_cache()
class Disease(object):
    ''' Disease class to define utility functions for diseases on the site. '''

    @classmethod
    def get_site_diseases(cls, tier=None, dis_list=None):
        '''
        Returns a list of disease documents separated into main and other based on tier
        or by specify a list of diseases.
        @type  tier: integer
        @keyword tier: Tier to filter diseases by (default: None).
        @type  dis_list: list
        @keyword dis_list: list of diseases (default: None).
        '''
        if dis_list is not None and len(dis_list) == 0:
            return ([], [])

        logger.debug('Accessing disease cache')
        if tier is not None:
            return (Disease.MAIN if tier == 0 else [], Disease.OTHER if tier == 1 else [])
        elif dis_list is not None and len(dis_list) > 0:
            dis_list = [d.upper() for d in dis_list]
            return ([d for d in Disease.MAIN if getattr(d, "code") in dis_list],
                    [d for d in Disease.OTHER if getattr(d, "code") in dis_list])
        else:
            return (Disease.MAIN, Disease.OTHER)

    @classmethod
    def get_site_disease_codes(cls, tier=None):
        '''
        Returns a list of disease codes separated into main and other based on tier
        @type  tier: integer
        @keyword tier: Tier to filter diseases by (default: None).
        '''
        (main, other) = cls.get_site_diseases(tier)
        main_dis_codes = [getattr(doc, "code") for doc in main]
        other_dis_codes = [getattr(doc, "code") for doc in other]
        return (sorted(main_dis_codes), sorted(other_dis_codes))
