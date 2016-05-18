''' API for the Elastic REST resources. '''
from rest_framework import serializers, viewsets
from elastic.rest_framework.resources import ListElasticMixin, ElasticLimitOffsetPagination,\
    RetrieveElasticMixin
from elastic.elastic_settings import ElasticSettings


class PublicationSerializer(serializers.Serializer):
    ''' Publication resource. '''

    class PublicationAuthor(serializers.Serializer):
        name = serializers.ReadOnlyField()
        initials = serializers.ReadOnlyField()

    pmid = serializers.IntegerField()
    title = serializers.ReadOnlyField()
    abstract = serializers.ReadOnlyField()
    journal = serializers.ReadOnlyField()
    authors = serializers.ListField(child=PublicationAuthor())
    date = serializers.DateField()
    tags = serializers.DictField()


class PublicationViewSet(RetrieveElasticMixin, ListElasticMixin, viewsets.ReadOnlyModelViewSet):
    """
    Returns a list of publications.
    ---
    list:
        response_serializer: PublicationSerializer
        parameters:
            - name: pmid
              description: PubMed ID (e.g. 20937630).
              required: false
              type: string
              paramType: query
            - name: title
              description: Title.
              required: false
              type: string
              paramType: query
            - name: authors__name
              description: Author names.
              required: false
              type: string
              paramType: query
            - name: tags__disease
              description: Disease tag (e.g. T1D).
              required: false
              type: string
              paramType: query
    """
    serializer_class = PublicationSerializer
    pagination_class = ElasticLimitOffsetPagination
    idx = ElasticSettings.idx('PUBLICATION')
    filter_fields = ('pmid', 'title', 'authors__name', 'tags__disease')
