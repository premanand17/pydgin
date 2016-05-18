''' Genome Browser '''
from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView

from browser import igv_settings


class BrowserView(TemplateView):
    ''' Renders the Genome Browser page. '''
    template_name = "browser/index.html"

    def get_context_data(self, **kwargs):
        context = super(BrowserView, self).get_context_data(**kwargs)
        genome = kwargs['genome'] if 'genome' in kwargs else self.request.GET.get('genome')
        if genome is None:
            genome = getattr(igv_settings, 'DEAFULT_GENOME')
        if genome == 'hg37':
            genome = 'hg19'
        genome_details = getattr(igv_settings, 'GENOME_DETAILS')[genome]
        if self.request.GET.get('loc') is not None:
            genome_details['locus'] = self.request.GET.get('loc')
        context['genome'] = genome
        context['title'] = genome_details['display_name']
        context['locus'] = genome_details['locus']
        context['genome_options'] = getattr(igv_settings, 'GENOME_DETAILS')

        context = BrowserView.get_tracks(self.request, genome, genome_details['tracks'], context)
        return context

    @classmethod
    def get_tracks(cls, request, genome, tracklist, context):
        if genome is None:
            messages.error(request, 'No genome given.')
            raise Http404()

        track_details = getattr(igv_settings, 'TRACK_DETAILS')
        track_settings = []
        for track in list(tracklist.keys()):
            for key in tracklist[track]:
                track_details[track][key] = tracklist[track][key]
            track_settings.append(track_details[track])

        context['tracks'] = track_settings
        return context
