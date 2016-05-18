''' Gene document. '''
import locale

from criteria.helper.criteria import Criteria
from django.core.urlresolvers import reverse

from core.document import FeatureDocument
from elastic.elastic_settings import ElasticSettings
from elastic.search import ElasticQuery, Search
from elastic.query import Query


class GeneDocument(FeatureDocument):
    ''' Gene document object. '''
    EXCLUDED_RESULT_KEYS = ['dbxrefs', 'start']

    def result_card_process_attrs(self):
        ''' Show only subset of dbxrefs. '''
        dbxrefs = getattr(self, 'dbxrefs')
        dbx = {}
        if 'ensembl' in dbxrefs:
            dbx['ensembl'] = dbxrefs['ensembl']
        if 'entrez' in dbxrefs:
            dbx['entrez'] = dbxrefs['entrez']
        setattr(self, 'dbxref', dbx)

        ''' remove 'dbxrefs.' from key highlights '''
        if self.highlight() is not None:
            new_highlight = {}
            for k, matches in self.highlight().items():
                new_highlight[k.replace('dbxrefs.', '')] = matches
            if new_highlight:
                self.__dict__['_meta']['highlight'] = new_highlight

    def result_card_keys(self):
        ''' Gets the keys of the document object as an ordered list to show in the result card. '''
        keys = super().result_card_keys()
        okeys = ['symbol', 'biotype', 'description']
        for key in keys:
            if key not in okeys:
                okeys.append(key)
        return okeys

    def get_position(self, **kwargs):
        return ("chr" + getattr(self, "chromosome") +
                ":" + str(locale.format("%d",  getattr(self, "start"), grouping=True)) +
                "-" + str(locale.format("%d", getattr(self, "stop"), grouping=True)))

    def get_chrom(self, **kwargs):
        return ("chr" + getattr(self, "chromosome"))

    def get_name(self):
        return getattr(self, "symbol")

    def get_sub_heading(self):
        return getattr(self, "description")

    def get_diseases(self):
        if super(GeneDocument, self).get_diseases():
            diseases = [getattr(d, "code") for d in Criteria.get_disease_tags(getattr(self, "dbxrefs")['ensembl'],
                                                                              idx=ElasticSettings.idx('GENE_CRITERIA'))]
            return diseases
        return []

    def get_link_id(self):
        ''' Id used in generating page link. '''
        return getattr(self, "dbxrefs")['ensembl']

    def url(self):
        ''' Document page. '''
        return reverse('gene_page') + '?g='

    def comparable(self):
        ''' Document(s) can be compared. '''
        return True

    @classmethod
    def get_genes(cls, ens_ids, sources=[]):
        ''' Get gene document(s) from a list of ensembl IDs. '''
        query = ElasticQuery(Query.ids(ens_ids), sources=sources)
        return Search(query, idx=ElasticSettings.idx('GENE', 'GENE'), size=len(ens_ids)).search().docs
