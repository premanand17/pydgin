''' Region views. '''

import json
import re
import gene

from django.contrib import messages
from django.http import Http404
from django.http.response import JsonResponse
from django.views.generic.base import TemplateView

from core.views import SectionMixin
from criteria.helper.region_criteria import RegionCriteria
from disease.utils import Disease
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query, Filter, BoolQuery, RangeQuery
from elastic.search import ElasticQuery, Search
from region.document import DiseaseLocusDocument, StudyHitDocument
from region.utils import Region


class RegionView(SectionMixin, TemplateView):
    ''' Renders a region page. '''
    template_name = "region/index.html"

    def get_context_data(self, **kwargs):
        context = super(RegionView, self).get_context_data(**kwargs)
        region = kwargs['region'] if 'region' in kwargs else self.request.GET.get('r')
        if region is None:
            messages.error(self.request, 'No region given.')
            raise Http404()

        if re.search("[p|q]\d+", region.lower()) is None:
            regionDocs = Region.loci_to_regions([region.lower()])
            if len(regionDocs) == 0:
                messages.error(self.request, 'No region found.')
                raise Http404()

            region = regionDocs[0].doc_id()
        return RegionView.get_region(self.request, region, context)

    @classmethod
    def get_region(cls, request, region, context):
        if region is None:
            messages.error(request, 'No region given.')
            raise Http404()
        query = ElasticQuery(Query.ids(region.split(',')))
        elastic = Search(query, idx=ElasticSettings.idx('REGION', 'REGION'), size=5)
        res = elastic.search()
        if res.hits_total == 0:
            messages.error(request, 'Region(s) '+region+' not found.')
        elif res.hits_total < 9:
            context['features'] = [Region.pad_region_doc(doc) for doc in res.docs]

            fids = [doc.doc_id() for doc in res.docs]
            criteria_disease_tags = RegionView.criteria_disease_tags(request, fids)
            context['criteria'] = criteria_disease_tags

            context['title'] = ', '.join([getattr(doc, 'region_name') for doc in res.docs])
            return context
        raise Http404()

    @classmethod
    def criteria_disease_tags(cls, request, qids):
        ''' Get criteria disease tags for a given ensembl ID for all criterias. '''
        criteria_disease_tags = RegionCriteria.get_all_criteria_disease_tags(qids)
        return criteria_disease_tags


def criteria_details(request):
    ''' Get criteria details for a given region ID. '''
    feature_id = request.POST.get('feature_id')
    criteria_details = RegionCriteria.get_criteria_details(feature_id)
    return JsonResponse(criteria_details)


class RegionTableView(TemplateView):
    '''Renders a table of all regions for a specific disease'''
    template_name = 'region/region_table.html'

    def get_context_data(self, **kwargs):
        context = super(RegionTableView, self).get_context_data(**kwargs)
        disease = kwargs['disease'] if 'disease' in kwargs else self.request.GET.get('d')
        return RegionTableView.get_regions(self.request, disease, context)

    @classmethod
    def get_regions(cls, request, dis, context):
        # is_authenticated = False
        elastic_url = ElasticSettings.url()

        (core, other) = Disease.get_site_diseases(dis_list=dis.upper().split(','))
        if len(core) == 0 and len(other) == 0:
            messages.error(request, 'Disease '+dis+' not found.')
            raise Http404()

        disease = core[0] if len(core) > 0 else other[0]
        context['title'] = getattr(disease, "name")+" Regions"

        docs = DiseaseLocusDocument.get_disease_loci_docs(dis)
        if len(docs) == 0:
            messages.error(request, 'No regions found for '+dis+'.')
            raise Http404()

        visible_hits = DiseaseLocusDocument.get_hits([h for r in docs for h in getattr(r, 'hits')])
        meta_response = Search.elastic_request(elastic_url, ElasticSettings.idx("IC_STATS") + '/_mapping',
                                               is_post=False)
        regions = []
        ens_all_cand_genes = []
        all_markers = []
        for r in docs:
            region = r.get_disease_region(visible_hits)
            if region is not None:
                ens_all_cand_genes.extend(region['ens_cand_genes'])
                all_markers.extend(region['markers'])
                region['hits'] = StudyHitDocument.process_hits(r.hit_docs, region['all_diseases'])

                (all_coding, all_non_coding) = get_genes_for_region(getattr(r, "seqid"),
                                                                    region['rstart']-500000, region['rstop']+500000)
                (region_coding, coding_up, coding_down) = _region_up_down(all_coding, region['rstart'], region['rstop'])
                (region_non_coding, non_coding_up, non_coding_down) = \
                    _region_up_down(all_non_coding, region['rstart'], region['rstop'])
                region['genes'] = {
                    'upstream': {'coding': coding_up, 'non_coding': non_coding_up},
                    'region': {'coding': region_coding, 'non_coding': region_non_coding},
                    'downstream': {'coding': coding_down, 'non_coding': non_coding_down},
                }
                regions.append(region)

        # look for pleiotropy by looking for diseases for the markers in IC_STATS and other study hits
        stats_query = ElasticQuery.filtered(Query.terms("marker", all_markers),
                                            Filter(RangeQuery("p_value", lte=5E-08)))
        stats_docs = Search(stats_query, idx=ElasticSettings.idx("IC_STATS"), size=len(all_markers)).search().docs

        # get ensembl to gene symbol mapping for all candidate genes
        all_cand_genes = gene.utils.get_gene_docs_by_ensembl_id(ens_all_cand_genes)
        for region in regions:
            region['cand_genes'] = {cg: all_cand_genes[cg] for cg in region.pop("ens_cand_genes", None)}
            (study_ids, region['marker_stats']) = _process_stats(stats_docs, region['markers'], meta_response)

            # add diseases from IC/GWAS stats
            region['all_diseases'].extend([getattr(mstat, 'disease') for mstat in region['marker_stats']])

            other_hits_query = ElasticQuery(
                        BoolQuery(must_arr=[RangeQuery("tier", lte=2), Query.terms("marker", region['markers'])],
                                  must_not_arr=[Query.terms("dil_study_id", study_ids)]))
            other_hits = Search(other_hits_query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'), size=100).search()
            region['extra_markers'] = StudyHitDocument.process_hits(other_hits.docs, region['all_diseases'])

        context['regions'] = regions
        context['disease_code'] = [dis]
        context['disease'] = getattr(disease, "name")
        return context


def _process_stats(stats_docs, markers, meta_response):
    ''' Proces IC stats. '''
    study_ids = []
    stats_result_docs = []
    for doc in stats_docs:
        if getattr(doc, 'marker') in markers:
            stats_result_docs.append(doc)
            elastic_meta = json.loads(meta_response.content.decode("utf-8"))
            meta_info = elastic_meta[doc.index()]['mappings'][doc.type()]['_meta']
            setattr(doc, "disease", meta_info['disease'])
            if re.match(r"^gdx", meta_info['study'].lower()):
                setattr(doc, "dil_study_id", meta_info['study'].replace('GDXHsS00', ''))
                study_ids.append(meta_info['study'])
            setattr(doc, "p_value", float(getattr(doc, "p_value")))
    return (study_ids, stats_result_docs)


def _region_up_down(genes, regions_start, regions_stop):
    ''' Separate into within region and upstream and downstream arrays.'''
    region = []
    up = []
    down = []
    for doc in genes:
        this_start = getattr(doc, "start")
        this_stop = getattr(doc, "stop")
        if((this_start > regions_start and this_start < regions_stop) or
           (this_stop > regions_start and this_stop < regions_stop) or
           (this_start < regions_start and this_stop > regions_stop)):
            region.append(doc)
        elif this_start < regions_start:
            down.append(doc)
        else:
            up.append(doc)
    return (region, up, down)


def get_genes_for_region(seqid, start, end, must=None):
    coding = []
    non_coding = []
    gene_index = ElasticSettings.idx('GENE', idx_type='GENE')
    elastic = Search.range_overlap_query(seqid=seqid.lower(), start_range=start, end_range=end,
                                         idx=gene_index, field_list=['start', 'stop', '_id', 'biotype', 'symbol'],
                                         seqid_param="chromosome", end_param="stop", size=10000)
    for doc in elastic.search().docs:
        if getattr(doc, "biotype") == "protein_coding":
            coding.append(doc)
        else:
            non_coding.append(doc)
    return (coding, non_coding)
