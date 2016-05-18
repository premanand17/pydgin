''' Define a resource for LD Rserve data to be used in Django REST framework. '''
from elastic.search import Search, ElasticQuery
from elastic.query import Query, BoolQuery
from elastic.elastic_settings import ElasticSettings
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.response import Response
from django.conf import settings
import pyRserve
import json
from elastic.rest_framework.elastic_obj import ElasticObject


class LDFilterBackend(OrderingFilter, DjangoFilterBackend):
    ''' Extend L{DjangoFilterBackend} for filtering LD resources. '''

    def filter_queryset(self, request, queryset, view):
        ''' Override this method to request just the documents required from Rserve. '''
        try:
            filterable = getattr(view, 'filter_fields', [])
            filters = dict([(k, v) for k, v in request.GET.items() if k in filterable])

            mid1 = filters.get('m1', 'rs2476601')
            dataset = filters.get('dataset', 'EUR').replace('-', '')
            mid2 = filters.get("m2")
            window_size = int(filters.get('window_size', 1000000))
            dprime = filters.get("dprime", 0.)
            rsq = filters.get("rsq", 0.8)
            maf = filters.get("maf", False)

            if maf:
                maf = True
            build_version = filters.get("build", 'GRCh38').lower()
            pos = filters.get("pos", False)
            if pos:
                pos = True

            query = ElasticQuery(BoolQuery(must_arr=[Query.term("id", mid1)]), sources=['seqid', 'start'])
            elastic = Search(search_query=query, idx=ElasticSettings.idx('MARKER', 'MARKER'), size=1)
            doc = elastic.search().docs[0]
            seqid = getattr(doc, 'seqid')

            rserve = getattr(settings, 'RSERVE')
            conn = pyRserve.connect(host=rserve.get('HOST'), port=rserve.get('PORT'))
            ld_str = conn.r.ld_run(dataset, seqid, mid1, marker2=mid2,
                                   window_size=window_size, dprime=dprime,
                                   rsq=rsq, maf=maf, position=pos, build_version=build_version)
            ld_str = ld_str.replace('D.prime', 'dprime').replace('R.squared', 'rsquared')
            conn.close()
            return [ElasticObject(initial=json.loads(str(ld_str)))]
        except (TypeError, ValueError, IndexError, ConnectionError):
            return [ElasticObject(initial={'ld': None})]


class ListLDMixin(object):
    ''' Get a list of markers in LD. '''
    filter_backends = [LDFilterBackend, ]

    def get_queryset(self):
        return None

    def list(self, request, *args, **kwargs):
        ''' Retrieve a list of documents. '''
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class PopulationFilterBackend(OrderingFilter, DjangoFilterBackend):
    ''' Extend L{DjangoFilterBackend} for filtering LD resources. '''

    def filter_queryset(self, request, queryset, view):
        ''' Override this method to request just the documents required from Rserve. '''
        try:
            filterable = getattr(view, 'filter_fields', [])
            filters = dict([(k, v) for k, v in request.GET.items() if k in filterable])

            mid1 = filters.get('marker', 'rs2476601')
            dataset = filters.get('dataset', 'EUR').replace('-', '')
            query = ElasticQuery(BoolQuery(must_arr=[Query.term("id", mid1)]), sources=['seqid', 'start'])
            elastic = Search(search_query=query, idx=ElasticSettings.idx('MARKER', 'MARKER'), size=1)
            doc = elastic.search().docs[0]
            seqid = getattr(doc, 'seqid')

            rserve = getattr(settings, 'RSERVE')
            conn = pyRserve.connect(host=rserve.get('HOST'), port=rserve.get('PORT'))
            pop_str = conn.r.get_pop(dataset, seqid, mid1)

            pops = json.loads(str(pop_str))
            populations = []
            for pop in pops:
                pops[pop]['population'] = pop
                populations.append(pops[pop])
            conn.close()
            return [ElasticObject(initial={'populations': populations, 'marker': mid1})]
        except (TypeError, ValueError, IndexError, ConnectionError):
            return [ElasticObject(initial={'populations': None, 'marker': mid1})]


class ListPopulationMixin(object):
    ''' Get a list of populations. '''
    filter_backends = [PopulationFilterBackend, ]

    def get_queryset(self):
        return None

    def list(self, request, *args, **kwargs):
        ''' Retrieve a list of documents. '''
        qs = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
