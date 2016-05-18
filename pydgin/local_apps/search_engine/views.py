''' Search engine views. '''
import logging
from operator import attrgetter
import re

from django.conf import settings
from django.http.response import JsonResponse, Http404
from django.shortcuts import render
from django.template.context_processors import csrf
from django.views.generic.base import TemplateView

from elastic.aggs import Agg, Aggs
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query, Filter, BoolQuery, ScoreFunction, FunctionScoreQuery, \
    ExistsFilter
from elastic.search import Search, ElasticQuery, Highlight, Suggest
from pydgin_auth.permissions import get_user_groups
from region.utils import Region


logger = logging.getLogger(__name__)


def suggester(request):
    ''' Provide auto suggestions. Ajax request returning a JSON response. '''
    query_dict = request.GET
    idx_dict = ElasticSettings.search_props(query_dict.get("idx"), request.user)
    suggester = ','.join(ElasticSettings.idx(k) for k in idx_dict['suggester_keys'])
    resp = Suggest.suggest(query_dict.get("term"), suggester, name='suggest', size=8)['suggest']
    return JsonResponse({"data": [opts['text'] for opts in resp[0]['options']]})


def search_page(request):
    ''' Renders a page to allow searches to be constructed. '''
    query_dict = request.GET
    if query_dict.get("query"):
        context = _search_engine(query_dict, request.POST, request.user)
        context['CDN'] = settings.CDN
        context.update(csrf(request))
        return render(request, 'search_engine/result.html', context,
                      content_type='text/html')
    raise Http404()


class AdvancedSearch(TemplateView):
    ''' Renders a advanced search page. '''
    template_name = "search_engine/advanced_search.html"

    def get_context_data(self, **kwargs):
        context = super(AdvancedSearch, self).get_context_data(**kwargs)
        context['section_options'] = {'collapse': False}
        return context


def _search_engine(query_dict, user_filters, user):
    ''' Carry out a search and add results to the context object. '''
    user_query = query_dict.get("query")
    query = _gene_lookup(user_query)

    source_filter = [
        'symbol', 'synonyms', "dbxrefs.*", 'biotype', 'description',  # gene
        'id', 'rscurrent', 'rshigh',                                  # marker
        'journal', 'title', 'tags.disease',                           # publication
        'name', 'code',                                               # disease
        'study_id', 'study_name',                                     # study
        'region_name', 'marker']                                      # regions

    if re.compile(r'^[0-9 ]+$').findall(query):
        source_filter.append('pmid')      # publication - possible PMID(s)
    search_fields = []
    maxsize = 20
    if user_filters.getlist("maxsize"):
        maxsize = int(user_filters.get("maxsize"))

    # build search_fields from user input filter fields
    for it in user_filters.items():
        if len(it) == 2:
            if it[0] == 'query':
                continue
            parts = it[1].split(":")
            if len(parts) == 3:
                search_fields.append(parts[1]+"."+parts[2])
            elif len(parts) == 2:
                search_fields.append(parts[1])

    if len(search_fields) == 0:
        search_fields = list(source_filter)
        search_fields.extend(['abstract', 'authors.name',   # publication
                              'authors', 'pmids',           # study
                              'markers', 'genes'])          # study/region
    source_filter.extend(['date', 'pmid', 'build_id', 'ref', 'alt', 'chr_band',
                          'disease_locus', 'disease_loci', 'region_id',
                          'seqid', 'start'])

    idx_name = query_dict.get("idx", 'ALL')
    idx_dict = ElasticSettings.search_props(idx_name, user)
    query_filters = _get_query_filters(user_filters, user)

    highlight = Highlight(search_fields, pre_tags="<strong>", post_tags="</strong>", number_of_fragments=0)
    sub_agg = Agg('idx_top_hits', 'top_hits', {"size": maxsize, "_source": source_filter,
                                               "highlight": highlight.highlight['highlight']})
    aggs = Aggs([Agg("idxs", "terms", {"field": "_index"}, sub_agg=sub_agg),
                 Agg("biotypes", "terms", {"field": "biotype", "size": 0}),
                 Agg("categories", "terms", {"field": "_type", "size": 0})])

    # create score functions
    score_fns = _build_score_functions(idx_dict)
    equery = BoolQuery(must_arr=Query.query_string(query, fields=search_fields),
                       should_arr=_auth_arr(user),
                       b_filter=query_filters,
                       minimum_should_match=1)

    search_query = ElasticQuery(FunctionScoreQuery(equery, score_fns, boost_mode='replace'))
    elastic = Search(search_query=search_query, aggs=aggs, size=0,
                     idx=idx_dict['idx'], idx_type=idx_dict['idx_type'])
    result = elastic.search()

    mappings = elastic.get_mapping()
    _update_mapping_filters(mappings, result.aggs)
    _update_biotypes(user_filters, result)

    return {'data': _top_hits(result), 'aggs': result.aggs,
            'query': user_query, 'idx_name': idx_name,
            'fields': search_fields, 'mappings': mappings,
            'hits_total': result.hits_total,
            'maxsize': maxsize, 'took': result.took}


def _build_score_functions(idx_dict):
    ''' Build an array of ScoreFunction instances for boosting query results. '''
    # create function score query to return documents with greater weights.
    score_fns = [ScoreFunction.create_score_function('field_value_factor', field='tags.weight', missing=1.0)]

    # create a function score that increases the score of markers.
    if ElasticSettings.idx('MARKER') is not None and ElasticSettings.idx('MARKER') in idx_dict['idx']:
        type_filter = Filter(Query({"type": {"value": ElasticSettings.get_idx_types('MARKER')['MARKER']['type']}}))
        score_fns.append(ScoreFunction.create_score_function('weight', 2, function_filter=type_filter.filter))
        logger.debug("Add marker type score function.")

    # create a function score that increases the score of publications tagged with disease.
    if ElasticSettings.idx('PUBLICATION') is not None and ElasticSettings.idx('PUBLICATION') in idx_dict['idx']:
        score_fns.append(ScoreFunction.create_score_function('weight', 2,
                                                             function_filter=ExistsFilter('tags.disease').filter))
        logger.debug("Add publication disease tag score function.")
    return score_fns


def _gene_lookup(search_term):
    ''' Look for any gene symbols (e.g. PTPN22) and get the corresponding
    Ensembl ID and append to query string '''
    if re.compile(r'[^\w\s\*]').findall(search_term):
        logger.debug('skip gene lookup as contains non-word pattern '+search_term)
        return search_term
    print('===============')
    print(search_term)
    words = re.sub("[^\w]", " ",  search_term)
    print(words)
    print('===============')
    equery = BoolQuery(b_filter=Filter(Query.query_string(words, fields=['symbol'])))
    search_query = ElasticQuery(equery, sources=['symbol'])
    (idx, idx_type) = ElasticSettings.idx('GENE', 'GENE').split('/')
    result = Search(search_query=search_query, size=10, idx=idx, idx_type=idx_type).search()
    if result.hits_total > 0:
        return ' '.join([doc.doc_id() for doc in result.docs]) + ' ' + search_term
    return search_term


def _top_hits(result):
    ''' Return the top hit docs in the aggregation 'idxs'. '''
    top_hits = result.aggs['idxs'].get_docs_in_buckets(obj_document=ElasticSettings.get_document_factory())
    idx_names = list(top_hits.keys())
    for idx in idx_names:
        idx_key = ElasticSettings.get_idx_key_by_name(idx)
        if idx_key.lower() != idx:
            if idx_key.lower() == 'marker':
                top_hits[idx]['doc_count'] = _collapse_marker_docs(top_hits[idx]['docs'])
            elif idx_key.lower() == 'region':
                top_hits[idx]['doc_count'] = _collapse_region_docs(top_hits[idx]['docs'])
            elif idx_key.lower() == 'publication':
                # sort by date
                top_hits[idx]['docs'].sort(key=attrgetter('date'), reverse=True)

            top_hits[idx_key.lower()] = top_hits[idx]
            del top_hits[idx]
    return top_hits


def _collapse_marker_docs(docs):
    ''' If the rsid document exists ignore results from immunochip and rs_merge
    for the same marker. '''
    rsids = [getattr(doc, 'id') for doc in docs if doc.type() == 'marker']
    rm_docs = [doc for doc in docs
               if doc.type() != 'marker' and (getattr(doc, 'id') in rsids or
                                              getattr(doc, 'rscurrent') in rsids)]
    for doc in rm_docs:
        docs.remove(doc)
    return len(docs)


def _collapse_region_docs(docs):
    ''' If the document is a hit then find parent region; pad all regions for build_info.'''
    hits = [doc for doc in docs if doc.type() == 'hits']
    regions = [doc for doc in docs if doc.type() == 'region']

    if len(hits) > 0:
        regions = Region.hits_to_regions(hits)
        for doc in hits:
            disease_locus = getattr(doc, "disease_locus")
            for region in regions:
                disease_loci = getattr(region, "disease_loci")
                if disease_locus in disease_loci:
                    region.__dict__['_meta']['highlight'] = doc.highlight()
            docs.remove(doc)

    regions = [Region.pad_region_doc(doc) for doc in regions]

    for doc in regions:
        if doc in docs:
            docs.remove(doc)
        docs.append(doc)

    return len(docs)


def _get_query_filters(q_dict, user):
    ''' Build query bool filter. If biotypes are specified add them to the filter and
    allow for other non-gene types.
    @type  q_dict: dict
    @param q_dict: request dictionary.
    '''
    if not q_dict.getlist("biotypes"):
        return None

    query_bool = BoolQuery()
    if q_dict.getlist("biotypes"):
        query_bool.should(Query.terms("biotype", q_dict.getlist("biotypes")))
        type_filter = [Query.query_type_for_filter(ElasticSettings.search_props(c.upper(), user)['idx_type'])
                       for c in q_dict.getlist("categories") if c != "gene"]
        if len(type_filter) > 0:
            query_bool.should(type_filter)
    return Filter(query_bool)


def _update_mapping_filters(mappings, aggs):
    ''' Change the mapping dictionary for displaying as a search filter. Remove indices
    from the mapping that have no results (using the category/type aggregation.
    Also use the index key rather than name.

    @type  mappings: dict
    @param mappings: Elastic indices mappings.
    @type  aggs: L{Aggs}
    @param aggs: Search query aggregation.
    '''
    idx_types = [agg['key'] for agg in aggs['categories'].get_buckets()]
    idx_names = list(mappings.keys())
    for idx in idx_names:
        idx_key = ElasticSettings.get_idx_key_by_name(idx)
        for t in mappings[idx]["mappings"].keys():
            if t in idx_types:
                mappings[idx_key] = mappings[idx]
                break
        del mappings[idx]


def _update_biotypes(user_filters, result):
    ''' Update the biotype aggregation based on those in the saved-biotypes
    data. This is used to maintain the list of biotypes when unchecked. '''
    biotypes = user_filters.getlist("saved-biotypes")
    search_buckets = result.aggs['biotypes'].get_buckets()
    for btype in biotypes:
        found = False
        for bucket in search_buckets:
            if bucket['key'] == btype:
                found = True
                break
        if not found:
            search_buckets.append({'key': btype, 'doc_count': 0})


def _auth_arr(user):
    ''' Get authentication array for BoolQuery for retrieving public and
    authenticated documents.  '''
    auth_arr = [Query.missing_terms("field", "group_name")]  # all public documents
    try:
        auth_arr.append(Query.terms("group_name",  # all documents in the user group
                        [gp.lower() for gp in get_user_groups(user)]).query_wrap())
    except Http404:
        # not logged in
        pass
    return auth_arr
