from django import template
from django.conf import settings

from core.document import FeatureDocument, PydginDocument, ResultCardMixin
from gene import utils


register = template.Library()


@register.filter
def db_link(db):
    ''' Look up a URL for a given database. '''
    settings
    db_names = settings.URL_LINKS.keys()
    if db.lower() in db_names:
        return settings.URL_LINKS[db]
    return ""


@register.filter
def is_list(val):
    ''' Is the value an instance of a list. '''
    return isinstance(val, list)


@register.filter
def replace_dot(val):
    ''' Replace dot in a string with undesrscore. '''
    return val.replace('.', '_')


@register.filter
def dict_lookup(d, key):
    return d[key]


@register.filter
def doc_name(doc):
    ''' Gets feature name '''
    return doc.get_name() if isinstance(doc, PydginDocument) \
        else settings.TEMPLATE_STRING_IF_INVALID


@register.filter
def doc_link_id(doc):
    ''' Get id used in lpage link. '''
    return doc.get_link_id() if isinstance(doc, ResultCardMixin) \
        else settings.TEMPLATE_STRING_IF_INVALID


@register.filter
def doc_url(doc):
    ''' Gets url to feature page. '''
    return doc.url() if isinstance(doc, ResultCardMixin) \
        else settings.TEMPLATE_STRING_IF_INVALID


@register.filter
def doc_ext(doc):
    ''' Is this an external source. '''
    return doc.is_external() if isinstance(doc, ResultCardMixin) \
        else settings.TEMPLATE_STRING_IF_INVALID


@register.filter
def doc_comparable(doc):
    ''' Can compare documents. '''
    return doc.comparable() if isinstance(doc, ResultCardMixin) \
        else settings.TEMPLATE_STRING_IF_INVALID


@register.filter
def doc_result_card_keys(doc):
    ''' Can compare documents. '''
    return doc.result_card_keys() if isinstance(doc, ResultCardMixin) \
        else settings.TEMPLATE_STRING_IF_INVALID


@register.filter
def current_position(doc):
    ''' Gets feature name '''
    return doc.get_position(build=38) if isinstance(doc, FeatureDocument) \
        else settings.TEMPLATE_STRING_IF_INVALID


@register.filter
def sub_heading(doc):
    ''' Gets feature sub-heading if defined '''
    return doc.get_sub_heading() if isinstance(doc, PydginDocument) \
        else settings.TEMPLATE_STRING_IF_INVALID


@register.filter
def diseases(doc):
    ''' Gets feature sub-heading if defined '''
    try:
        return doc.get_diseases() if isinstance(doc, PydginDocument) \
            else settings.TEMPLATE_STRING_IF_INVALID
    except TypeError:
        return {}


@register.filter
def location(doc):
    ''' Gets feature sub-heading if defined '''
    return doc.get_position() if isinstance(doc, FeatureDocument) \
        else settings.TEMPLATE_STRING_IF_INVALID


@register.filter
def chromosome(doc):
    ''' Gets feature chromosome if defined '''
    return doc.get_chrom() if isinstance(doc, FeatureDocument) \
        else settings.TEMPLATE_STRING_IF_INVALID


@register.filter
def ens2sym(ens_ids):
    ''' Convert ensembl IDs to gene symbols. '''
    return utils.get_gene_docs_by_ensembl_id(ens_ids)
