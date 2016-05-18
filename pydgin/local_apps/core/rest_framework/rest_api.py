''' Core DRF web-services. '''
from rest_framework import serializers, mixins
from core.rest_framework.feature_resources import ListLocationsMixin
from rest_framework.viewsets import GenericViewSet


class LocationsSerializer(serializers.Serializer):
    ''' Serializer for locations. '''
    feature = serializers.CharField(help_text='feature')
    chr = serializers.CharField(help_text='chromosome')
    start = serializers.IntegerField(help_text='start position')
    end = serializers.IntegerField(help_text='end position')
    locusString = serializers.CharField(help_text='locus')


class LocationsViewSet(ListLocationsMixin, mixins.ListModelMixin, GenericViewSet):
    ''' Given a feature (e.g. gene, marker, region) and the build return the location(s).
    ---
    list:
        response_serializer: LocationsSerializer
        parameters:
            - name: feature
              description: gene, marker or region (e.g. IL2, rs2476601).
              required: false
              type: string
              paramType: query
            - name: build
              description: genome build (e.g. hg38).
              required: false
              type: string
              paramType: query
    '''
    serializer_class = LocationsSerializer
    filter_fields = ('feature', 'build')
