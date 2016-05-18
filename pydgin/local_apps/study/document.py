'''' Study Document. '''
from criteria.helper.criteria import Criteria
from django.core.urlresolvers import reverse
from elastic.elastic_settings import ElasticSettings

from core.document import PydginDocument
from elastic.query import BoolQuery, Query
from elastic.search import ElasticQuery, Search
from elastic.result import Document


class StudyDocument(PydginDocument):
    ''' Study document object. '''
    EXCLUDED_RESULT_KEYS = ['study_id', 'description']

    def get_name(self):
        return getattr(self, "study_id")

    def get_sub_heading(self):
        return getattr(self, "study_name")

    def get_diseases(self):
        ''' Overridden get diseases for feature. '''
        if super(StudyDocument, self).get_diseases():
            diseases = [getattr(d, "code") for d in
                        Criteria.get_disease_tags(self.get_name(), idx=ElasticSettings.idx('STUDY_CRITERIA'))]
            return diseases
        return []

    def get_link_id(self):
        ''' Page link id. '''
        return self.get_name()

    def url(self):
        ''' Document page link. '''
        return reverse('study_page_params') + '?s='

    @classmethod
    def get_studies(cls, study_ids=None, disease_code=None, sources=[], split_name=True):
        studies_query = ElasticQuery(Query.match_all(), sources=sources)
        if disease_code is not None:
            studies_query = ElasticQuery(BoolQuery(must_arr=Query.term("diseases", disease_code)), sources=sources)
        elif study_ids:
            studies_query = ElasticQuery(Query.ids(study_ids), sources=sources)
        studies = Search(studies_query, idx=ElasticSettings.idx('STUDY', 'STUDY'), size=200).search().docs
        for doc in studies:
            if split_name and getattr(doc, 'study_name') is not None:
                setattr(doc, 'study_name', getattr(doc, 'study_name').split(':', 1)[0])
        return Document.sorted_alphanum(studies, "study_id")
