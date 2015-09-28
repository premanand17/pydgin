''' Define search engine urls. '''
from django.conf.urls import url
from search_engine import views

urlpatterns = [
        url(r'^$', views.search_page, name='search_page'),
        url(r'^suggest$', views.suggester, name='suggester'),
    ]
