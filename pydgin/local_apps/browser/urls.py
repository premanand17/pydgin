''' Define genome browser urls. '''
from django.conf.urls import url

from browser.views import BrowserView


urlpatterns = [
    url(r'^$', BrowserView.as_view(), name='browser_params'),
    url(r'^(?P<genome>.*)/$', BrowserView.as_view(), name='browser')
]
