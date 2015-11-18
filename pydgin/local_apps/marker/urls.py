''' Define search engine urls. '''
from django.conf.urls import url
from marker import views

urlpatterns = [
        url(r'^$', views.marker_page, name='marker_page'),
    ]
