
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render
from elastic.search import ElasticQuery, Search
from elastic.query import Query
from elastic.elastic_settings import ElasticSettings


def marker_page(request):
    ''' Renders a gene page. '''
    query_dict = request.GET
    marker = query_dict.get("m")
    if marker is None:
        messages.error(request, 'No gene name given.')
        raise Http404()
    query = ElasticQuery(Query.match('id', marker))
    elastic = Search(query, idx=ElasticSettings.idx('MARKER', 'MARKER'), size=5)
    res = elastic.search()
    if res.hits_total == 1:
        context = {'marker': res.docs[0]}
        return render(request, 'marker/marker.html', context,
                      content_type='text/html')
    elif res.hits_total == 0:
        messages.error(request, 'Marker '+marker+' not found.')
        raise Http404()
