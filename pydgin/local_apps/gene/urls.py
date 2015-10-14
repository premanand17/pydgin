''' Define search engine urls. '''
from django.conf.urls import url
from gene import views

urlpatterns = [
    url(r'^$', views.gene_page, name='gene_page'),
    url(r'^publications/$', views.pub_details, name='pub_details'),
    url(r'^interactions/$', views.interaction_details, name='interaction_details'),
    url(r'^genesets/$', views.genesets_details, name='genesets'),
    url(r'^studies/$', views.studies_details, name='studies'),
]
