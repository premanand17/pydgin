import locale
import logging
import sys

from criteria.helper.criteria import Criteria
from django.conf import settings
from django.core.urlresolvers import reverse
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query, BoolQuery, Filter, RangeQuery, OrFilter, \
    FilteredQuery
from elastic.rest_framework.elastic_obj import ElasticObject
from elastic.result import Document
from elastic.search import ElasticQuery, Search

from core.document import FeatureDocument, PydginDocument
from gene import utils
from pydgin import pydgin_settings
from region.utils import Region


logger = logging.getLogger(__name__)


class RegionDocument(FeatureDocument):
    ''' An extension of a FetaureDocument for a Region. '''
    EXCLUDED_RESULT_KEYS = ['hits', 'pmids', 'disease_loci', 'region_id', 'region_name',
                            'tier', 'species', 'seqid', 'build_info', 'studies', 'tags']

    def get_name(self):
        ''' Override get document name. '''
        return getattr(self, "region_name")

    def get_link_id(self):
        ''' Id used in generating page link. '''
        return getattr(self, "region_id")

    def url(self):
        ''' Document page. '''
        return reverse('region_page_params') + '?r='

    def get_position(self, build=pydgin_settings.DEFAULT_BUILD):
        build_info = getattr(self, "build_info")
        if build_info['build'] == build:
            return ("chr" + build_info['seqid'] + ":" + str(locale.format("%d", build_info['start'], grouping=True)) +
                    "-" + str(locale.format("%d", build_info['end'], grouping=True)))
        else:
            return None

    def get_sub_heading(self):
        ''' Overridden get feature sub-heading. '''
        return ""

    def get_diseases(self):
        ''' Overridden get diseases for feature. '''
        if super(RegionDocument, self).get_diseases():
            idx = ElasticSettings.idx('REGION_CRITERIA')
            diseases = [getattr(d, "code") for d in Criteria.get_disease_tags(getattr(self, "region_id"), idx=idx)]
            return diseases
        return []

    def result_card_keys(self):
        ''' Gets the keys of the document object as an ordered list to show in the result card. '''
        keys = super().result_card_keys()
        okeys = ['genes', 'markers', 'location']
        for key in keys:
            if key not in okeys:
                okeys.append(key)
        return okeys

    def result_card_process_attrs(self):
        ''' Show only subset of dbxrefs. '''
        if getattr(self, 'build_info') is not None:
            setattr(self, 'location', self.get_position())

        ''' show genes and marker highlights '''
        if self.highlight() is not None:
            new_highlight = {}
            for k, matches in self.highlight().items():
                if k != 'marker' and k != 'genes':
                    continue
                attr_key = 'genes' if k == 'genes' else 'markers'
                features = getattr(self, attr_key)
                for m in matches:
                    match = m.replace('<strong>', '').replace('</strong>', '')
                    features = [feat if feat != match else m for feat in getattr(self, attr_key)]
                new_highlight[attr_key] = ['; '.join(features)]

            if new_highlight:
                self.__dict__['_meta']['highlight'] = new_highlight

    def get_disease_loci(self):
        ''' Returns the disease loci for requested hit docs '''
        regions_idx = ElasticSettings.idx('REGION', 'DISEASE_LOCUS')
        disease_loci = getattr(self, "disease_loci")
        if len(disease_loci) == 0:
            logger.warning("no disease_locus attributes found/given")
            return
        resultObj = Search(search_query=ElasticQuery(Query.ids(disease_loci)),
                           idx=regions_idx).search()
        return resultObj.docs

    @classmethod
    def get_hits_by_study_id(cls, study_id, sources=[]):
        ''' Get visible/authenticated hits. '''
        hits_query = ElasticQuery(BoolQuery(must_arr=Query.term('dil_study_id', study_id),
                                            b_filter=Filter(Query.missing_terms("field", "group_name"))),
                                  sources=sources)
        docs = Search(hits_query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'), size=1000).search().docs
        ens_ids = [gene for doc in docs if getattr(doc, 'genes') for gene in getattr(doc, 'genes')]
        gene_docs = utils.get_gene_docs_by_ensembl_id(ens_ids, ['symbol'])
        for doc in docs:
            if getattr(doc, 'genes'):
                genes = {}
                for ens_id in getattr(doc, 'genes'):
                    try:
                        genes[ens_id] = getattr(gene_docs[ens_id], 'symbol')
                    except KeyError:
                        genes = {ens_id: ens_id}
                setattr(doc, 'genes', genes)
            build_info = getattr(doc, 'build_info')
            for bi in build_info:
                if bi['build'] == settings.DEFAULT_BUILD:
                    setattr(doc, "loc", "chr" + bi['seqid'] + ":" +
                            str(locale.format("%d", bi['start'], grouping=True)) + "-" +
                            str(locale.format("%d", bi['end'], grouping=True)))
        return docs


class StudyHitDocument(FeatureDocument):
    ''' An extension of a FeatureDocument for a Study Hit. '''

    def get_name(self):
        return getattr(self, "chr_band")

    def get_position(self, build=pydgin_settings.DEFAULT_BUILD):
        build_info = getattr(self, "build_info")
        for b in build_info:
            if b['build'] == build:
                return ("chr" + b['seqid'] + ":" + str(locale.format("%d", b['start'], grouping=True)) +
                        "-" + str(locale.format("%d", b['end'], grouping=True)))
        return None

    @classmethod
    def get_overlapping_hits(self, build, seqid, start, end):
        query_bool = BoolQuery(must_arr=[RangeQuery("build_info.start", lte=start),
                                         RangeQuery("build_info.end", gte=end)])
        or_filter = OrFilter(RangeQuery("build_info.start", gte=start, lte=end))
        or_filter.extend(RangeQuery("build_info.end", gte=start, lte=end)) \
                 .extend(query_bool)
        range_query = FilteredQuery(BoolQuery(must_arr=[Query.term("build_info.seqid", seqid),
                                                        Query.term("build_info.build", build)]),
                                    or_filter)

        query = ElasticQuery.filtered_bool(
            Query.nested("build_info", range_query),
            BoolQuery(must_arr=[RangeQuery("tier", lte=2)]),
            # sources=["disease", "marker", "chr_band", "tier", "build_info", "disease_locus"]
            )
        elastic = Search(search_query=query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'))
        return elastic.search().docs

    @classmethod
    def get_overlapping_features(self, build, seqid, start, end):

        features = []
        study_hits = self.get_overlapping_hits(build, seqid, start, end)
        if len(study_hits) == 0:
            return features

        regions = Region.hits_to_regions(study_hits)
        for doc in regions:
            doc = Region.pad_region_doc(doc)
            loc = doc.get_position(build=build).split(':')
            pos = loc[1].replace(',', '').split('-')
            feature = {
                'name': doc.get_name(),
                'id': doc.doc_id(),
                'chr': loc[0],
                'start': int(pos[0]),
                'end': int(pos[1]) if len(pos) > 1 else int(pos[0]),
                'strand': doc.get_strand_as_int(),
                'attributes': {}
            }
            loci = doc.get_disease_loci()
            sub_features = []
            for locus in loci:
                attributes = {}
                loc = locus.get_position(build=build).split(':')
                pos = loc[1].replace(',', '').split('-')
                sub_feature = {
                    'name': locus.get_name(),
                    'id': locus.doc_id(),
                    'chr': loc[0],
                    'start': int(pos[0]),
                    'end': int(pos[1]) if len(pos) > 1 else int(pos[0]),
                    'strand': locus.get_strand_as_int()
                }
                if hasattr(locus, "disease") and getattr(locus, "disease") is not None:
                    attributes['disease'] = getattr(locus, "disease")
                sub_feature['attributes'] = attributes
                sub_features.append(sub_feature)
            feature['sub_features'] = sub_features
            features.append(ElasticObject(feature))

        return features

    @classmethod
    def process_hits(cls, docs, diseases):
        ''' Process docs to add disease, P-values, odds ratios. '''
        build = pydgin_settings.DEFAULT_BUILD
        for h in docs:
            if h.disease is not None and h.disease not in diseases:
                diseases.append(h.disease)

            setattr(h, 'dil_study_id', getattr(h, 'dil_study_id').replace('GDXHsS00', ''))

            for build_info in getattr(h, "build_info"):
                if build_info['build'] == build:
                    setattr(h, "current_pos", "chr" + build_info['seqid'] + ":" +
                            str(locale.format("%d", build_info['start'], grouping=True)) +
                            "-" + str(locale.format("%d", build_info['end'], grouping=True)))

            setattr(h, "p_value", None)
            if getattr(h, "p_values")['combined'] is not None:
                setattr(h, "p_value", float(getattr(h, "p_values")['combined']))
                setattr(h, "p_val_src", "C")
            elif getattr(h, "p_values")['discovery'] is not None:
                setattr(h, "p_value", float(getattr(h, "p_values")['discovery']))
                setattr(h, "p_val_src", "D")

            setattr(h, "odds_ratio", None)
            setattr(h, "or_bounds", None)
            setattr(h, "risk_allele", None)
            if getattr(h, "odds_ratios")['combined']['or'] != None:
                setattr(h, "odds_ratio", getattr(h, "odds_ratios")['combined']['or'])
                setattr(h, "or_src", "C")
                or_combined = getattr(h, "odds_ratios")['combined']
                if or_combined['upper'] != None:
                    if float(or_combined['or']) > 1:
                        setattr(h, "or_bounds", "("+or_combined['lower']+"-"+or_combined['upper']+")")
                    else:
                        setattr(h, "or_bounds", "("+str(float("{0:.2f}".format(1/float(or_combined['upper'])))) + "-" +
                                str(float("{0:.2f}".format(1/float(or_combined['lower']))))+")")

            or_discovery = getattr(h, "odds_ratios")['discovery']
            if or_discovery['or'] != None:
                setattr(h, "odds_ratio", or_discovery['or'])
                setattr(h, "or_src", "D")
                if or_discovery['upper'] != None:
                    if float(or_discovery['or']) > 1:
                        setattr(h, "or_bounds", "("+or_discovery['lower']+"-"+or_discovery['upper']+")")
                    else:
                        setattr(h, "or_bounds", "("+str(float("{0:.2f}".format(1/float(or_discovery['upper'])))) + "-" +
                                str(float("{0:.2f}".format(1/float(or_discovery['lower']))))+")")

            if getattr(h, "odds_ratio") is not None:
                if float(getattr(h, "odds_ratio")) > 1:
                    setattr(h, "risk_allele", getattr(h, "alleles")['minor'])
                else:
                    setattr(h, "odds_ratio", str(float("{0:.2f}".format(1/float(getattr(h, "odds_ratio"))))))
                    setattr(h, "risk_allele", getattr(h, "alleles")['major'])
        return docs


class DiseaseLocusDocument(FeatureDocument):

    @classmethod
    def get_disease_loci_docs(cls, disease):
        ''' Get sorted list of DiseaseLocusDocument's. '''
        query = ElasticQuery(Query.term("disease", disease.lower()))
        disease_loci_docs = Search(query, idx=ElasticSettings.idx('REGION', 'DISEASE_LOCUS'), size=500).search().docs
        return Document.sorted_alphanum(disease_loci_docs, 'seqid')

    @classmethod
    def get_hits(cls, hit_ids, sources=[]):
        ''' Get visible/authenticated hits. '''
        hits_query = ElasticQuery(BoolQuery(must_arr=Query.ids(hit_ids),
                                            b_filter=Filter(Query.missing_terms("field", "group_name"))))
        return Search(hits_query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'), size=len(hit_ids)).search().docs

    def get_name(self):
        return getattr(self, "region_name")

    def get_position(self, build=pydgin_settings.DEFAULT_BUILD):
        ''' Get position of disease locus '''
        disease_locus = self.get_disease_region(build=build)
        if disease_locus is not None:
            return (disease_locus['seqid'] + ":" + disease_locus['start'] + "-" + disease_locus['end'])
        return None

    def get_disease_region(self, visible_hits=None, build=pydgin_settings.DEFAULT_BUILD):
        ''' Get the disease region object by combining the hits. '''
        hits = getattr(self, "hits")
        if visible_hits is None:
            visible_hits = DiseaseLocusDocument.get_hits([h for h in hits])

        regions_start = sys.maxsize
        regions_stop = 0
        self.hit_docs = []
        for h in visible_hits:
            if h.doc_id() in hits:
                self.hit_docs.append(h)
                build_info = getattr(h, 'build_info')
                for info in build_info:
                    if info['build'] == build:
                        if info['start'] < regions_start:
                            regions_start = info['start']
                        if info['end'] > regions_stop:
                            regions_stop = info['end']

        if len(self.hit_docs) < 1:
            return None

        ens_cand_genes = {g for h in self.hit_docs if h.genes is not None for g in h.genes}
        return {
            'region_name': getattr(self, "region_name"),
            'locus_id': getattr(self, "locus_id"),
            'seqid': 'chr'+getattr(self, "seqid"),
            'rstart': regions_start,
            'rstop': regions_stop,
            'start': str(locale.format("%d", regions_start, grouping=True)),
            'end': str(locale.format("%d", regions_stop, grouping=True)),
            'all_diseases': [getattr(self, 'disease')],
            'markers': list(set([h.marker for h in self.hit_docs])),
            'ens_cand_genes': ens_cand_genes
        }
