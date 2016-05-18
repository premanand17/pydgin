''' Define a resource for LD Rserve data to be used in Django REST framework. '''
from django.conf import settings
from django.http.response import Http404
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.response import Response

from elastic.elastic_settings import ElasticSettings
from elastic.query import Query, BoolQuery
from elastic.rest_framework.elastic_obj import ElasticObject
from elastic.search import Search, ElasticQuery
from region.document import RegionDocument
from region.utils import Region


class LocationsFilterBackend(OrderingFilter, DjangoFilterBackend):
    ''' Extend L{DjangoFilterBackend} for filtering LD resources. '''

    BUILD_MAP = {
        'hg18': 36,
        'hg19': 27,
        'hg38': 38
    }

    def _get_build(self, build):
        ''' Given the build return the build number as an integer. '''
        for hg, b in LocationsFilterBackend.BUILD_MAP.items():
            if hg == build:
                return b
        return int(build)

    def filter_queryset(self, request, queryset, view):
        ''' Override this method to request feature locations. '''
        try:
            filterable = getattr(view, 'filter_fields', [])
            filters = dict([(k, v) for k, v in request.GET.items() if k in filterable])
            query_str = filters.get('feature', 'PTPN22')
            build = self._get_build(filters.get('build', settings.DEFAULT_BUILD))
            if query_str is None or query_str == '':
                return [ElasticObject(initial={'error': 'No feature name provided.'})]

            search_fields = ['id',
                             'symbol', 'dbxrefs.ensembl',
                             'region_name']
            sources = ['start', 'stop', 'seqid', 'chromosome',
                       'disease_loci']
            idxs = ElasticSettings.getattr('IDX')
            MARKER_IDX = ''

            if build == ElasticSettings.get_label('MARKER', label='build'):
                MARKER_IDX = 'MARKER'
            if MARKER_IDX == '':
                for idx in idxs:
                    if 'MARKER' in idx:
                        if build == ElasticSettings.get_label(idx, label='build'):
                            MARKER_IDX = idx

            (idx, idx_type) = ElasticSettings.idx_names(MARKER_IDX, 'MARKER')
            (idx_r, idx_type_r) = ElasticSettings.idx_names('REGION', 'REGION')
            (idx_g, idx_type_g) = ElasticSettings.idx_names('GENE', 'GENE')
            idx += ',' + idx_r + ',' + idx_g
            idx_type += ',' + idx_type_r + ',' + idx_type_g

            equery = BoolQuery(must_arr=Query.query_string(query_str, fields=search_fields))
            elastic = Search(search_query=ElasticQuery(equery, sources), size=10, idx=idx, idx_type=idx_type)
            docs = elastic.search().docs
            locs = []
            for doc in docs:
                if isinstance(doc, RegionDocument):
                    doc = Region.pad_region_doc(doc)

                loc = doc.get_position(build=build).split(':')
                pos = loc[1].replace(',', '').split('-')
                locs.append(ElasticObject(
                    {'feature': query_str,
                     'chr': loc[0],
                     'start': int(pos[0]),
                     'end': int(pos[1]) if len(pos) > 1 else int(pos[0]),
                     'locusString': query_str+" ("+str(loc[1])+")"}))
            return locs
        except (TypeError, ValueError, IndexError, ConnectionError):
            raise Http404


class ListLocationsMixin(object):
    ''' Get a list of locations for a feature. '''
    filter_backends = [LocationsFilterBackend, ]

    def get_queryset(self):
        return None

    def list(self, request, **kwargs):
        ''' Retrieve a list of documents. '''
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
