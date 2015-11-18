"""pydgin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from pydgin import views, rest_api
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings

# restful framework
router = routers.DefaultRouter()
router.register(r'pubs', rest_api.PublicationViewSet, base_name='pubs')

urlpatterns = [
    url(r'^{}/admin/'.format(settings.ADMIN_URL_PATH), include(admin.site.urls)),
    url(r'^accounts/', include('pydgin_auth.urls', namespace="accounts")),
    url(r'^$', views.index, name='index'),
    url(r'^search/', include('search_engine.urls')),
    url(r'^gene/', include('gene.urls')),
    url(r'^marker/', include('marker.urls')),
    url(r'^rest/', include(router.urls, namespace="rest")),
    url(r'^rest-docs/', include('rest_framework_swagger.urls')),
    url(r'^api-token-auth/', obtain_auth_token),
    url(r'^auth_test/', include('auth_test.urls', namespace="auth_test")),
]
