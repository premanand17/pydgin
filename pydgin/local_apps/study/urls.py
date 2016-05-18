''' Define study urls. '''
from django.conf.urls import url

from study.views import StudyView, StudySectionView
from study import views


urlpatterns = [
    url(r'^$', StudyView.as_view(), name='study_page_params'),
    url(r'^section/$', StudySectionView.as_view(), name='study_section'),
    url(r'^criteria/$', views.criteria_details, name='criteria'),
    url(r'^(?P<study>.*)/$', StudyView.as_view(), name='study_page'),
]
