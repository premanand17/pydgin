''' Marker page view. '''
import logging
import re

from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.http.response import JsonResponse
from django.views.generic.base import TemplateView
from elastic.aggs import Agg, Aggs
from elastic.elastic_settings import ElasticSettings
from elastic.exceptions import SettingsError
from elastic.query import Query
from elastic.result import Document
from elastic.search import ElasticQuery, Search, ScanAndScroll

from core.document import PydginDocument
from core.views import SectionMixin
from criteria.helper.marker_criteria import MarkerCriteria


logger = logging.getLogger(__name__)


class MarkerView(SectionMixin, TemplateView):
    ''' Renders a marker page. '''
    template_name = "marker/index.html"

    def get_context_data(self, **kwargs):
        context = super(MarkerView, self).get_context_data(**kwargs)
        marker = kwargs['marker'] if 'marker' in kwargs else self.request.GET.get('m')
        return MarkerView.get_marker(self.request, marker, context)

    @classmethod
    def get_marker(cls, request, marker, context):
        if marker is None:
            messages.error(request, 'No marker name given.')
            raise Http404()

        fields = ['id', 'rscurrent'] if marker.startswith("rs") else ['name']
        sub_agg = Agg('top_hits', 'top_hits', {"size": 15})
        aggs = Aggs(Agg("types", "terms", {"field": "_type"}, sub_agg=sub_agg))
        query = ElasticQuery(Query.query_string(marker, fields=fields))
        elastic = Search(search_query=query, idx=ElasticSettings.idx('MARKER'), aggs=aggs, size=0)
        res = elastic.search()
        title = ''
        if res.hits_total >= 1:
            types = getattr(res.aggs['types'], 'buckets')
            marker_doc = None
            ic_docs = []
            history_docs = []
            for doc_type in types:
                hits = doc_type['top_hits']['hits']['hits']
                for hit in hits:
                    doc = PydginDocument.factory(hit)
                    if doc.get_name() is not None:
                        title = doc.get_name()

                    if 'marker' == doc_type['key']:
                        marker_doc = doc
                    elif 'immunochip' == doc_type['key']:
                        ic_docs.append(doc)
                    elif 'rs_merge' == doc_type['key']:
                        history_docs.append(doc)

            if marker_doc is not None:
                marker_doc.marker_build = _get_marker_build(ElasticSettings.idx('MARKER'))

            criteria_disease_tags = MarkerView.criteria_disease_tags(request, [marker])
            context['criteria'] = criteria_disease_tags
            context['features'] = [marker_doc]
            context['old_dbsnp_docs'] = _get_old_dbsnps(marker)
            context['ic'] = ic_docs
            context['history'] = history_docs
            context['title'] = title
            return context
        elif res.hits_total == 0:
            messages.error(request, 'Marker '+marker+' not found.')
            raise Http404()

    @classmethod
    def criteria_disease_tags(cls, request, qids):
        ''' Get criteria disease tags for a given ensembl ID for all criterias. '''
        criteria_disease_tags = MarkerCriteria.get_all_criteria_disease_tags(qids)
        return criteria_disease_tags


MARKER_PATTERN = re.compile('^MARKER_\d+')


def _get_old_dbsnps(marker):
    ''' Get markers from old versions of DBSNP. Assumes the index key is
    prefixed by 'MARKER_\d+'. eg: MARKER_138'''
    old_dbsnps_names = sorted([ElasticSettings.idx(k) for k in ElasticSettings.getattr('IDX').keys()
                               if MARKER_PATTERN.match(k)], reverse=True)

    old_dbsnp_docs = []
    if len(old_dbsnps_names) > 0:
        search_query = ElasticQuery(Query.query_string(marker, fields=['id', 'rscurrent']))
        for idx_name in old_dbsnps_names:
            elastic2 = Search(search_query=search_query, idx=idx_name, idx_type='marker')
            docs = elastic2.search().docs
            if len(docs) > 0:
                old_doc = docs[0]
                old_doc.marker_build = _get_marker_build(idx_name)
                old_dbsnp_docs.append(old_doc)
    return old_dbsnp_docs


def _get_marker_build(idx_name):
    ''' Get the marker build as defined in the settings. '''
    try:
        idx_key = ElasticSettings.get_idx_key_by_name(idx_name)
        return ElasticSettings.get_label(idx_key, label='build')
    except (KeyError, SettingsError, TypeError):
        logger.error('Marker build not identified from ELASTIC settings.')
        return ''


def association_stats(request, sources=None):
    ''' Get association statistics for a given marker ID. '''
    seqid = request.GET.get('chr').replace('chr', '')
    idx_type = request.GET.get('idx_type').upper()
    data = []

    def get_stats(resp_json):
        hits = resp_json['hits']['hits']
        for hit in hits:
            d = Document(hit)
            data.append({
                "CHROM": getattr(d, 'seqid'),
                "POS": getattr(d, 'position'),
                "PVALUE": getattr(d, 'p_value'),
                "DBSNP_ID": getattr(d, 'marker')
            })

    query = ElasticQuery(Query.query_string(seqid, fields=["seqid"]), sources=sources)
    ScanAndScroll.scan_and_scroll(ElasticSettings.idx('IC_STATS', idx_type), call_fun=get_stats, query=query)

    json = {"variants": data}
    return JsonResponse(json)


def criteria_details(request):
    ''' Get criteria details for a given marker ID. '''
    feature_id = request.POST.get('feature_id')
    criteria_details = MarkerCriteria.get_criteria_details(feature_id)
    return JsonResponse(criteria_details)


class LDView(TemplateView):
    ''' Renders a LD tool page. '''
    template_name = "marker/ld_tool.html"

    def get_context_data(self, **kwargs):
        context = super(LDView, self).get_context_data(**kwargs)
        context['section_options'] = {'collapse': False}
        return context


class JSTestView(TemplateView):
    ''' Renders a test marker page. '''
    template_name = "js_test/ld.html"

    def get_context_data(self, **kwargs):
        context = super(JSTestView, self).get_context_data(**kwargs)
        if not (settings.DEBUG or settings.TESTMODE):
            raise Http404()
        return context
