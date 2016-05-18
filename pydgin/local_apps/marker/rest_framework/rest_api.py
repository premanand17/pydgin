''' API for the RServe REST resources. '''
from rest_framework import serializers, mixins
from rest_framework.viewsets import GenericViewSet
from marker.rest_framework.rserve_resources import ListLDMixin, ListPopulationMixin


class LDSerializer(serializers.Serializer):
    ''' Rserve LD resource. '''

    class LD(serializers.Serializer):
        marker2 = serializers.CharField(help_text='marker 2')
        dprime = serializers.FloatField(help_text='D prime')
        rsquared = serializers.FloatField(help_text='R squared')
        MAF = serializers.FloatField(required=False, help_text='Minor allele frequency')
        major = serializers.CharField(required=False, help_text='major allele')
        minor = serializers.CharField(required=False, help_text='minor allele')
        position = serializers.IntegerField(required=False, help_text='Position of variant 2')

    ld = LD(many=True, help_text='list of marker(s) in LD')


class LDViewSet(ListLDMixin, mixins.ListModelMixin, GenericViewSet):
    """
    Returns markers in LD with a given variant.
    ---
    list:
        response_serializer: LDSerializer
        parameters:
            - name: m1
              description: marker (e.g. rs2476601) to identify markers in LD with.
              required: true
              type: string
              paramType: query
            - name: m2
              description: optional marker to calculate LD for marker1, Defaults to NULL.
              required: false
              type: string
              paramType: query
            - name: window_size
              description: window size to look for markers in LD, Defaults to 1000000.
              required: false
              type: integer
              paramType: query
            - name: dprime
              description: dprime to use, Defaults to 0.
              required: false
              type: float
              paramType: query
            - name: rsq
              description: R square threshold, Defaults to 0.8.
              required: false
              type: float
              paramType: query
            - name: build
              description: Genome build, e.g grch38.
              required: false
              type: string
              paramType: query
            - name: maf
              description: if TRUE report the MAF in the result.
              required: false
              type: boolean
              paramType: query
            - name: pos
              description: if TRUE report the position in the result.
              required: false
              type: boolean
              paramType: query
    """
    serializer_class = LDSerializer
    lookup_url_kwarg = "m1"
    lookup_fields = ('m1')
    filter_fields = ('m1', 'dataset', 'm2', 'window_size', 'dprime',
                     'rsq', 'maf', 'build', 'pos')


class PopulationsSerializer(serializers.Serializer):
    ''' Rserve population resource. '''

    class Population(serializers.Serializer):
        population = serializers.CharField(required=False, help_text='population')
        MAF = serializers.FloatField(required=False, help_text='Minor allele frequency')
        major = serializers.CharField(required=False, help_text='major allele')
        minor = serializers.CharField(required=False, help_text='minor allele')

    populations = Population(many=True, help_text='population details (major/minor allele, MAF)')
    marker = serializers.CharField(help_text='marker')


class PopulationsViewSet(ListPopulationMixin, mixins.ListModelMixin, GenericViewSet):
    """ Returns population stats for a given variant.
    ---
    list:
        response_serializer: PopulationsSerializer
        parameters:
            - name: marker
              description: marker (e.g. rs2476601) to identify markers in LD with.
              required: false
              type: string
              paramType: query
    """
    serializer_class = PopulationsSerializer
    filter_fields = ('marker')
