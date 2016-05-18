''' Define a resource for LD Rserve data to be used in Django REST framework. '''
from django.conf import settings
from django.http.response import Http404
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.response import Response

from region.document import DiseaseLocusDocument, StudyHitDocument
from django.contrib import messages
from region import views
from elastic.search import ElasticQuery, Search
from elastic.query import Query, Filter, RangeQuery, BoolQuery
from elastic.elastic_settings import ElasticSettings
from elastic.result import Document
from gene.document import GeneDocument


class RegionsFilterBackend(OrderingFilter, DjangoFilterBackend):
    ''' Extend L{DjangoFilterBackend} for filtering LD resources. '''

    BUILD_MAP = {
        'hg18': 36,
        'hg19': 37,
        'hg38': 38
    }

    def _get_build(self, build):
        ''' Given the build return the build number as an integer. '''
        for hg, b in RegionsFilterBackend.BUILD_MAP.items():
            if hg == build:
                return b
        return int(build)

    def filter_queryset(self, request, queryset, view):
        ''' Get disease regions. '''
        try:
            filterable = getattr(view, 'filter_fields', [])
            filters = dict([(k, v) for k, v in request.GET.items() if k in filterable])
            dis = filters.get('disease', 'T1D')
            show_genes = filters.get('genes', False)
            show_markers = filters.get('markers', False)
            show_regions = filters.get('regions', True)

            build = self._get_build(filters.get('build', settings.DEFAULT_BUILD))
            docs = DiseaseLocusDocument.get_disease_loci_docs(dis)
            if len(docs) == 0:
                messages.error(request, 'No regions found for '+dis+'.')

            visible_hits = DiseaseLocusDocument.get_hits([h for r in docs for h in getattr(r, 'hits')])
            regions = []
            all_markers = []
            all_genes = []
            ens_all_cand_genes = []
            for r in docs:
                region = r.get_disease_region(visible_hits, build=build)
                if region is not None:
                    ens_all_cand_genes.extend(region['ens_cand_genes'])
                    all_markers.extend(region['markers'])
                    region['hits'] = [self._study_hit_obj(s, region) for s in
                                      StudyHitDocument.process_hits(r.hit_docs, region['all_diseases'])]

                    (all_coding, all_non_coding) = views.get_genes_for_region(getattr(r, "seqid"),
                                                                              region['rstart']-500000,
                                                                              region['rstop']+500000)
                    (region_coding, coding_up, coding_down) = views._region_up_down(all_coding, region['rstart'],
                                                                                    region['rstop'])
                    (region_non_coding, non_coding_up, non_coding_down) = \
                        views._region_up_down(all_non_coding, region['rstart'], region['rstop'])
                    region['genes'] = {
                        'upstream': {'coding': [g.doc_id() for g in coding_up],
                                     'non_coding': [g.doc_id() for g in non_coding_up]},
                        'region': {'coding': [g.doc_id() for g in region_coding],
                                   'non_coding': [g.doc_id() for g in region_non_coding]},
                        'downstream': {'coding': [g.doc_id() for g in coding_down],
                                       'non_coding': [g.doc_id() for g in non_coding_down]},
                    }
                    all_genes.extend(region['genes']['region']['coding'])
                    all_genes.extend(region['genes']['region']['non_coding'])
                    regions.append(region)

            # look for pleiotropy by looking for diseases for the markers in IC_STATS and other study hits
            stats_query = ElasticQuery.filtered(Query.terms("marker", all_markers),
                                                Filter(RangeQuery("p_value", lte=5E-08)))
            stats_docs = Search(stats_query, idx=ElasticSettings.idx("IC_STATS"), size=len(all_markers)).search().docs
            meta_response = Search.elastic_request(ElasticSettings.url(), ElasticSettings.idx("IC_STATS") + '/_mapping',
                                                   is_post=False)
            # get ensembl to gene symbol mapping for all candidate genes
            extra_markers = []
            for region in regions:
                # add diseases from IC/GWAS stats
                (study_ids, region['marker_stats']) = views._process_stats(stats_docs, region['markers'], meta_response)
                region['all_diseases'].extend([getattr(mstat, 'disease') for mstat in region['marker_stats']])

                other_hits_query = ElasticQuery(
                        BoolQuery(must_arr=[RangeQuery("tier", lte=2), Query.terms("marker", region['markers'])],
                                  must_not_arr=[Query.terms("dil_study_id", study_ids)]))
                other_hits = Search(other_hits_query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'),
                                    size=100).search()
                region['extra_markers'] = [self._study_hit_obj(s, region) for s in
                                           StudyHitDocument.process_hits(other_hits.docs, region['all_diseases'])]
                region['all_diseases'] = list(set(region['all_diseases']))
                extra_markers.extend([m['marker_id'] for m in region['extra_markers']])

            # get markers
            marker_objs = []
            if show_markers:
                query = ElasticQuery(Query.terms("id", all_markers), sources=['id', 'start'])
                marker_docs = Search(search_query=query, idx=ElasticSettings.idx('MARKER', 'MARKER'),
                                     size=len(all_markers)).search().docs
                mids = {getattr(m, 'id'): getattr(m, 'start') for m in marker_docs}
                marker_objs = [h for r in regions for h in r['hits']]
                marker_objs.extend([h for r in regions for h in r['extra_markers']])
                for m in marker_objs:
                    m['start'] = mids[m['marker_id']]

            # get genes
            gene_objs = []
            if show_genes:
                all_genes.extend(ens_all_cand_genes)
                gene_docs = GeneDocument.get_genes(all_genes, sources=['start', 'stop', 'chromosome',
                                                                       'symbol', 'biotype'])
                for doc in Document.sorted_alphanum(gene_docs, 'chromosome'):
                    ensembl_id = doc.doc_id()
                    region_name = ''
                    candidate_gene = 0
                    for region in regions:
                        if ('genes' in region and
                            (ensembl_id in region['genes']['region']['coding'] or
                             ensembl_id in region['genes']['region']['non_coding'] or
                             ensembl_id in region['ens_cand_genes'])):
                            region_name = region['region_name']
                            candidate_gene = 1 if ensembl_id in region['ens_cand_genes'] else 0
                            break
                    gene_objs.append({
                        'ensembl_id': ensembl_id,
                        'seqid': 'chr'+getattr(doc, 'chromosome'),
                        'start': getattr(doc, 'start'),
                        'end': getattr(doc, 'stop'),
                        'symbol': getattr(doc, 'symbol'),
                        'biotype': getattr(doc, 'biotype'),
                        'region_name': region_name,
                        'candidate_gene': candidate_gene
                    })
            if show_regions == 'false':
                regions = []
            regions.extend(gene_objs)
            regions.extend(marker_objs)
            return regions
        except (TypeError, ValueError, IndexError, ConnectionError) as e:
            print(e)
            raise Http404

    def _study_hit_obj(self, study, region):
        p = getattr(study, 'current_pos').split(':')
        rstart = p[1].split('-')[0]
        return {
            'region_name': region['region_name'],
            'marker_id': getattr(study, 'marker'),
            'pmid': getattr(study, 'pmid'),
            'disease': getattr(study, 'disease'),
            'study_id': 'GDXHsS00'+getattr(study, 'dil_study_id'),
            'chr_band': getattr(study, 'chr_band'),
            'position': getattr(study, 'current_pos'),
            'seqid': p[0],
            'start': rstart,
            'alleles': getattr(study, 'alleles'),
            'p_val_src': getattr(study, 'p_val_src'),
            'p_value': getattr(study, 'p_value'),
            'odds_ratio': getattr(study, 'odds_ratio'),
            'risk_allele': getattr(study, 'risk_allele'),
        }


class ListRegionsMixin(object):
    ''' Get a list of locations for a feature. '''
    filter_backends = [RegionsFilterBackend, ]

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
