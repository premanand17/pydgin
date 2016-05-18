''' Define search engine urls. '''
from django.conf.urls import url
from search_engine import views
from search_engine.views import AdvancedSearch

urlpatterns = [
        url(r'^$', views.search_page, name='search_page'),
        url(r'^advanced$', AdvancedSearch.as_view(), name='advanced_search_page'),
        url(r'^suggest$', views.suggester, name='suggester'),
    ]
