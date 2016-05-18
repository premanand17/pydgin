''' Marker documents.'''
from criteria.helper.criteria import Criteria
from django.core.urlresolvers import reverse
from elastic.elastic_settings import ElasticSettings

from core.document import FeatureDocument


class MarkerDocument(FeatureDocument):
    ''' Marker document object.'''
    EXCLUDED_RESULT_KEYS = ['seqid', 'start']

    def get_name(self):
        return getattr(self, "id")

    def get_position(self, **kwargs):
        return "chr" + getattr(self, "seqid") + ":" + str(getattr(self, "start"))

    def get_link_id(self):
        ''' Page link id. '''
        return self.get_name()

    def url(self):
        return reverse('marker_page') + '?m='

    def get_diseases(self):
        if super(MarkerDocument, self).get_diseases():
            diseases = [getattr(d, "code") for d in Criteria.get_disease_tags(self.get_name(),
                                                                              idx=ElasticSettings.idx('MARKER_CRITERIA'))]
            return diseases
        return []

    def get_sub_heading(self):
        return ""

    def result_card_process_attrs(self):
        ''' Show only subset of dbxrefs. '''
        if getattr(self, 'seqid') is not None:
            location = 'chr' + getattr(self, 'seqid')
            if hasattr(self, 'start'):
                location += ':' + str(getattr(self, 'start'))
            setattr(self, 'location', location)

    def result_card_keys(self):
        ''' Gets the keys of the document object as an ordered list to show in the result card. '''
        keys = super().result_card_keys()
        try:
            keys.remove('alt')
            keys.remove('ref')
            keys.extend(['alt', 'ref'])
        except ValueError:
            pass
        return keys


class ImmunoChipDocument(MarkerDocument):
    ''' ImmunoChip marker document. '''

    def get_name(self):
        return getattr(self, "name")
