from django import template
from django.conf import settings

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


@register.inclusion_tag('gene/pub_section.html')
def show_pub_section(gene):
    ''' Template inclusion tag to render a publication section given a
    list of PMIDs. '''
    return {'gene': gene}


@register.inclusion_tag('gene/studies_section.html')
def show_studies_section(ens_id):
    ''' Template inclusion tag to render an studies section given a
    ensembl ID. '''
    return {'ens_id': ens_id}


@register.inclusion_tag('gene/interactions_section.html')
def show_interactions_section(ens_id):
    ''' Template inclusion tag to render an interaction section given a
    ensembl ID. '''
    return {'ens_id': ens_id}


@register.inclusion_tag('gene/genesets_section.html')
def show_genesets_section(ens_id):
    ''' Template inclusion tag to render an interaction section given a
    ensembl ID. '''
    return {'ens_id': ens_id}


@register.inclusion_tag('gene/phenotype_section.html')
def show_phenotype_section(dbxrefs):
    if 'mmusculus' in dbxrefs['orthologs']:
        return {'mgi': dbxrefs['orthologs']['mmusculus']['MGI']}
    return {}


@register.filter
def div(value, divisor):
    ''' Divides the value by divisor. '''
    try:
        value = int(value)
        divisor = int(divisor)
        return int(value/divisor)
    except:
        pass
    return ''
