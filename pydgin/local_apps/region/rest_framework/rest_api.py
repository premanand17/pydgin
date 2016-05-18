''' Region DRF web-services. '''
from rest_framework import serializers, mixins, renderers
from region.rest_framework.region_resources import ListRegionsMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
import csv
from six import StringIO


class GeneCategory(serializers.Serializer):
    ''' Genes found in and up/downstream of the region. '''
    region = serializers.DictField(required=False)
    downstream = serializers.DictField(required=False)
    upstream = serializers.DictField(required=False)


class DiseaseRegionSerializer(serializers.Serializer):
    ''' Serializer for locations. '''

    # marker documents
    marker_id = serializers.CharField(help_text='marker_id', required=False)
    pmid = serializers.CharField(help_text='publication', required=False)
    alleles = serializers.DictField(help_text='alleles', required=False)
    disease = serializers.CharField(help_text='disease', required=False)
    p_value = serializers.CharField(help_text='p_value', required=False)
    odds_ratio = serializers.CharField(help_text='odds_ratio', required=False)
    study_id = serializers.CharField(help_text='study id', required=False)

    # gene documents
    ensembl_id = serializers.CharField(help_text='ensembl_id', required=False)
    biotype = serializers.CharField(help_text='biotype', required=False)
    symbol = serializers.CharField(help_text='symbol', required=False)
    candidate_gene = serializers.CharField(help_text='candidate gene', required=False)

    # regions
    region_name = serializers.CharField(help_text='region_name', required=False)
    seqid = serializers.CharField(help_text='chromosome')
    start = serializers.IntegerField(help_text='start position')
    end = serializers.IntegerField(help_text='end position', required=False)
    all_diseases = serializers.ListField(help_text='all diseases', required=False)
    markers = serializers.ListField(help_text='markers', required=False)
    ens_cand_genes = serializers.ListField(help_text='candidate genes', required=False)
    genes = GeneCategory(required=False)


class GFFRenderer(renderers.BaseRenderer):
    ''' Render GFF format. '''
    media_type = 'text/gff'
    format = 'gff'

    def render(self, data, media_type=None, renderer_context=None):
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer, delimiter="\t")
        header = self.header(renderer_context['request'])
        for hdr in header:
            csv_writer.writerow([hdr])

        for row in data:
            csv_writer.writerow(self.row_data(row))
        return csv_buffer.getvalue()

    def row_data(self, row):
        ''' GFF row data. '''
        raise NotImplementedError("Inheriting class should implement this method")

    def header(self, request):
        ''' List of GFF header lines. '''
        return ['##gff-version 3']


class DiseaseRegionGFFRenderer(GFFRenderer):
    ''' Render regions as in GFF format. '''
    def row_data(self, row):
        if 'marker_id' in row:
            attrs = 'Name='+row['marker_id']+';region_name='+row['region_name'] + \
                    ';major='+row['alleles']['major']+';minor='+row['alleles']['minor'] + \
                    ';p_value='+row['p_value'] + \
                    (';odds_ratio='+row['odds_ratio'] if row['odds_ratio'] is not None else '') + \
                    ";PMID="+row['pmid']

            return [row['seqid'], 'PUBMED', 'variant', row['start'], row['start'],
                    '.', '.', '.', attrs]
        elif 'ensembl_id' in row:
            return [row['seqid'], 'immunobase', row['biotype'], row['start'], row['end'],
                    '.', '.', '.',
                    'Name='+row['ensembl_id']+';region_name='+row['region_name']+';symbol='+row['symbol'] +
                    ';candidate_gene='+row['candidate_gene']
                    ]
        else:
            return [row['seqid'], 'immunobase', 'region', row['start'], row['end'],
                    '.', '.', '.',
                    'Name='+row['region_name']+';genes='+','.join(row['ens_cand_genes']) +
                    ';markers='+','.join(row['markers']) +
                    ';diseases='+','.join(row['all_diseases'])]

    def header(self, request):
        disease = request.GET.get('disease', 'T1D')
        return ['##gff-version 3', '##'+disease+' Regions from immunobase.org']


class DiseaseRegionViewSet(ListRegionsMixin, mixins.ListModelMixin, GenericViewSet):
    ''' Get the regions associated with a given disease (e.g. T1D, MS).
    ---
    list:
        response_serializer: DiseaseRegionSerializer
        parameters:
            - name: disease
              description: disease
              required: false
              type: string
              paramType: query
              defaultValue: 'T1D'
              enum: ['AS', 'ATD', 'CEL', 'CRO', 'JIA', 'MS', 'PBC', 'PSO', 'RA', 'SLE', 'T1D',
                     'UC', 'AA', 'IBD', 'IGE', 'NAR', 'PSC', 'SJO', 'SSC', 'VIT']
            - name: build
              description: genome build (e.g. hg38).
              required: false
              type: string
              paramType: query
              defaultValue: 'hg38'
              enum: ['hg38']
            - name: regions
              defaultValue: true
              enum: [false, true]
              description: show disease region positions
              type: boolean
            - name: genes
              defaultValue: false
              enum: [false, true]
              description: show gene positions
              type: boolean
            - name: markers
              defaultValue: false
              enum: [false, true]
              description: show marker positions
              type: boolean
        produces:
            - application/json
            - text/gff
    '''
    renderer_classes = (JSONRenderer, DiseaseRegionGFFRenderer, BrowsableAPIRenderer, )
    serializer_class = DiseaseRegionSerializer
    filter_fields = ('disease', 'build', 'genes', 'markers', 'regions')
