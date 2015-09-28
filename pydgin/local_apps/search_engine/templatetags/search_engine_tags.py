''' Template tags for the search engine app. '''
from django import template
from elastic.elastic_settings import ElasticSettings
from elastic.result import Document
from django.conf import settings
import re

register = template.Library()


@register.inclusion_tag('search_engine/search_engine_section.html', takes_context=True)
def show_search_engine(context):
    ''' Template inclusion tag to render search engine form. '''
    return {'index': ElasticSettings.search_props(user=context['request'].user)['idx_keys']}


@register.filter
def doc_highlight(doc):
    ''' Gets the highlighted section and split into fragments for parsing
    html tags as safe. '''
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID

    if doc.highlight() is None:
        return ''

    html_fragments = {}
    for key, values in doc.highlight().items():
        html_fragments[key] = []
        for value in values:
            v = re.split('(<strong>|</strong>)', value)
            html_fragments[key].extend(v)
    return html_fragments


@register.filter
def doc_highlight_keys(doc):
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID
    if doc.highlight() is None:
        return ''
    return doc.highlight().keys()
