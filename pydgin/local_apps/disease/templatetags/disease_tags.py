''' Template tags for the disease app. '''
from django import template
from elastic.elastic_settings import ElasticSettings
from elastic.search import ElasticQuery, Search
from elastic.query import Query, BoolQuery
from elastic.result import Document
from disease.utils import Disease

register = template.Library()


@register.filter
def keyvalue(dic, key):
    try:
        return dic[key]
    except KeyError:
        return ''


@register.inclusion_tag('disease/disease_bar.html')
def show_disease_bar(dis_list=None, expand_od=False, selected=None, href="/disease/"):
    ''' Template inclusion tag to render disease bar. '''
    if type(dis_list) is str:
        dis_list = [dis_list]
    (main, other) = Disease.get_site_diseases(dis_list=dis_list)
    return {'dis_main': main, 'dis_other': other, 'text': True, 'selected': selected, 'href': href,
            'expand_od': expand_od}


@register.inclusion_tag('disease/disease_bar.html')
def show_small_disease_bar(dis_list=None, href="/disease/"):
    ''' Template inclusion tag to render disease bar. '''
    (main, other) = Disease.get_site_diseases(dis_list=dis_list)
    if len(other) > 0:
        main.append(Document({"_source": {"code": "OD", "colour": "grey", "name": "Other Diseases"}}))
    return {'dis_main': main, 'text': False, 'href': href}


@register.inclusion_tag('disease/disease_code.html')
def show_disease(disease, scores, text=True, selected=None, href="/disease/"):
    ''' Template inclusion tag to render disease bar. '''
    if isinstance(disease, str):
        if disease == 'OD':
            disease = Document({"_source": {"code": "OD", "colour": "grey", "name": "Other Diseases"}})
        else:
            query = ElasticQuery(BoolQuery(should_arr=[Query.term('code', disease.lower()),
                                                       Query.term('name', disease.lower())]))
            disease = Search(query, idx=ElasticSettings.idx('DISEASE'), size=1).search().docs[0]
    score = ''
    if scores != '':
        score = scores[0]
    return {'disease': disease, 'score': score, 'text': text, 'selected': selected, 'href': href}
