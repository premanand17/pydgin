''' Core DRF web-services. '''
from rest_framework import serializers, mixins
from rest_framework.viewsets import GenericViewSet

from core.rest_framework.feature_resources import ListLocationsMixin, \
    ListFeaturesMixin


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


class FeatureSerializer(serializers.Serializer):
    ''' Serializer for locations. '''
    chr = serializers.CharField(help_text='chromosome')
    start = serializers.IntegerField(help_text='start position')
    end = serializers.IntegerField(help_text='end position')
    strand = serializers.IntegerField(help_text='strand')
    name = serializers.CharField(help_text='feature name')
    id = serializers.CharField(help_text='feature id')
    # biotype = serializers.CharField(help_text='biotype')
    # stain = serializers.CharField(help_text='stain')
    # alleles = serializers.CharField(help_text='alleles')
    attributes = serializers.DictField(help_text='feature attributes')
    sub_features = serializers.ListField(help_text="sub-features")


class FeatureViewSet(ListFeaturesMixin, mixins.ListModelMixin, GenericViewSet):
    ''' Given a feature type (e.g. gene, marker, region), build and genomic range
    return the location(s) & basic details or all features in the region.
    ---
    list:
        response_serializer: FeatureSerializer
        parameters:
            - name: ftype
              description: gene, marker or region.
              required: true
              type: string
              paramType: query
            - name: build
              description: genome build (e.g. hg38).
              required: true
              type: string
              paramType: query
            - name: chr
              description: chromosome (e.g. chr1).
              required: true
              type: string
              paramType: query
            - name: start
              description: start position.
              required: false
              type: integer
              paramType: query
            - name: end
              description: end position.
              required: false
              type: integer
              paramType: query
    '''
    serializer_class = FeatureSerializer
    filter_fields = ('ftype', 'build', 'chr', 'start', 'end')
