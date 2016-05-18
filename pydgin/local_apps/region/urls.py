''' Define region urls. '''
from django.conf.urls import url

from region import views
from region.views import RegionView, RegionTableView


urlpatterns = [
    url(r'^table/$', RegionTableView.as_view(), name='region_table_params'),
    url(r'^table/(?P<disease>.*)/$', RegionTableView.as_view(), name='region_table'),
    url(r'^$', RegionView.as_view(), name='region_page_params'),
    url(r'^criteria/$', views.criteria_details, name='criteria'),
    url(r'^(?P<region>.*)/$', RegionView.as_view(), name='region_page'),
]
