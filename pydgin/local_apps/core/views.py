''' Core view class mixins. '''
from django.conf import settings
from collections import OrderedDict


class SectionMixin(object):
    ''' Adds sections to the view context. '''

    def get_context_data(self, **kwargs):
        context = super(SectionMixin, self).get_context_data(**kwargs)
        sections_name = self.sections_name if hasattr(self, 'sections_name') else self.__class__.__name__
        context['sections'] = OrderedDict([(k, v) for k, v in
                                           settings.PAGE_SECTIONS[sections_name].items()
                                           if (isinstance(v, dict) and v['show']) or v])
        return context
