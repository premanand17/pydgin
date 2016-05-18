''' Gene views. '''
from django.http.response import JsonResponse
from elastic.search import ElasticQuery, Search
from elastic.query import Query, Filter
from elastic.elastic_settings import ElasticSettings
from django.http import Http404
from django.contrib import messages
from django.conf import settings
from core.views import SectionMixin
from django.views.generic.base import TemplateView
from gene import utils
from criteria.helper.gene_criteria import GeneCriteria


class GeneView(SectionMixin, TemplateView):
    ''' Renders a gene page. '''
    template_name = "gene/index.html"

    def get_context_data(self, **kwargs):
        context = super(GeneView, self).get_context_data(**kwargs)
        gene = kwargs['gene'] if 'gene' in kwargs else self.request.GET.get('g')
        return GeneView.get_gene(self.request, gene, context)

    @classmethod
    def get_gene(cls, request, gene, context):
        if gene is None:
            messages.error(request, 'No gene name given.')
            raise Http404()
        res = Search(search_query=ElasticQuery(Query.ids(gene.split(','))),
                     idx=ElasticSettings.idx('GENE', 'GENE'), size=9).search()
        if res.hits_total == 0:
            messages.error(request, 'Gene(s) '+gene+' not found.')
        elif res.hits_total < 9:
            context['features'] = res.docs
            fids = [doc.doc_id() for doc in res.docs]
            criteria_disease_tags = GeneView.criteria_disease_tags(request, fids)
            context['criteria'] = criteria_disease_tags
            context['title'] = ', '.join([getattr(doc, 'symbol') for doc in res.docs])
            return context
        raise Http404()

    @classmethod
    def criteria_disease_tags(cls, request, qids):
        ''' Get criteria disease tags for a given ensembl ID for all criterias. '''
        criteria_disease_tags = GeneCriteria.get_all_criteria_disease_tags(qids)
        return criteria_disease_tags


def pub_details(request):
    ''' Get PMID details. '''
    pmids = request.POST.getlist("pmids[]")
    query = ElasticQuery(Query.ids(pmids))
    elastic = Search(query, idx=ElasticSettings.idx('PUBLICATION', 'PUBLICATION'), size=len(pmids))
    return JsonResponse(elastic.get_json_response()['hits'])


def interaction_details(request):
    ''' Get interaction details for a given ensembl ID. '''
    ens_id = request.POST.get('ens_id')
    query = ElasticQuery.has_parent('gene', Query.ids(ens_id))
    elastic = Search(query, idx=ElasticSettings.idx('GENE', 'INTERACTIONS'), size=500)

    interaction_hits = elastic.get_json_response()['hits']
    ens_ids = []
    for hit in interaction_hits['hits']:
        for interactor in hit['_source']['interactors']:
            ens_ids.append(interactor['interactor'])
    docs = utils.get_gene_docs_by_ensembl_id(ens_ids, ['symbol'])
    for hit in interaction_hits['hits']:
        for interactor in hit['_source']['interactors']:
            iid = interactor['interactor']
            try:
                interactor['symbol'] = getattr(docs[iid], 'symbol')
            except KeyError:
                interactor['symbol'] = iid

    return JsonResponse(interaction_hits)


def genesets_details(request):
    ''' Get pathway gene sets for a given ensembl ID. '''
    ens_id = request.POST.get('ens_id')
    geneset_filter = Filter(Query.query_string(ens_id, fields=["gene_sets"]).query_wrap())
    query = ElasticQuery.filtered(Query.match_all(), geneset_filter)
    elastic = Search(query, idx=ElasticSettings.idx('GENE', 'PATHWAY'), size=500)
    genesets_hits = elastic.get_json_response()['hits']
    ens_ids = []
    for hit in genesets_hits['hits']:
        for ens_id in hit['_source']['gene_sets']:
            ens_ids.append(ens_id)
    docs = utils.get_gene_docs_by_ensembl_id(ens_ids, ['symbol'])

    for hit in genesets_hits['hits']:
        genesets = {}
        for ens_id in hit['_source']['gene_sets']:
            try:
                genesets[ens_id] = getattr(docs[ens_id], 'symbol')
            except KeyError:
                genesets[ens_id] = ens_id
        hit['_source']['gene_sets'] = genesets
    return JsonResponse(genesets_hits)


def criteria_details(request):
    ''' Get criteria details for a given ensembl ID. '''
    ens_id = request.POST.get('feature_id')
    criteria_details = GeneCriteria.get_criteria_details(ens_id)
    return JsonResponse(criteria_details)


class JSTestView(TemplateView):
    ''' Renders a marker page. '''
    template_name = "js_test/test.html"

    def get_context_data(self, **kwargs):
        context = super(JSTestView, self).get_context_data(**kwargs)
        if not (settings.DEBUG or settings.TESTMODE):
            raise Http404()
        return context
