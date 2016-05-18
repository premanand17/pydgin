''' Disease views. '''
import json

from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView

from elastic.elastic_settings import ElasticSettings
from elastic.query import Query, Filter, RangeQuery, BoolQuery
from elastic.search import ElasticQuery, Search
import gene
from region.document import DiseaseLocusDocument
from study.document import StudyDocument
from core.document import PublicationDocument


class DiseaseView(TemplateView):
    ''' Renders a disease page. '''
    template_name = "disease/index.html"

    def get_context_data(self, **kwargs):
        context = super(DiseaseView, self).get_context_data(**kwargs)
        disease = kwargs['disease'] if 'disease' in kwargs else self.request.GET.get('d')
        return DiseaseView.get_disease(self.request, disease, context)

    @classmethod
    def get_disease(cls, request, disease, context):
        disease = disease.lower()
        if disease is None:
            messages.error(request, 'No disease given.')
            raise Http404()
        query = ElasticQuery(Query.terms("code", [disease.split(',')]))
        elastic = Search(query, idx=ElasticSettings.idx('DISEASE', 'DISEASE'), size=5)
        res = elastic.search()
        if res.hits_total == 0:
            messages.error(request, 'Disease(s) '+disease+' not found.')
        elif res.hits_total < 9:
            disease_docs = res.docs
            names = ', '.join([getattr(doc, 'name') for doc in disease_docs])

            meta_response = Search.elastic_request(ElasticSettings.url(), ElasticSettings.idx("IC_STATS") + '/_mapping',
                                                   is_post=False)
            elastic_meta = json.loads(meta_response.content.decode("utf-8"))
            disease_docs = res.docs
            for dis in disease_docs:
                dis_code = getattr(dis, 'code').upper()
                docs = DiseaseLocusDocument.get_disease_loci_docs(dis_code)
                regions = []
                ens_all_cand_genes = []
                all_markers = []
                for r in docs:
                    region = r.get_disease_region()
                    if region is not None:
                        regions.append(region)
                        ens_all_cand_genes.extend(region['ens_cand_genes'])
                        all_markers.extend(region['markers'])

                # get ensembl to gene symbol mapping for all candidate genes
                all_cand_genes = gene.utils.get_gene_docs_by_ensembl_id(ens_all_cand_genes)
                for region in regions:
                    region['cand_genes'] = {cg: all_cand_genes[cg] for cg in region.pop("ens_cand_genes", None)}
                setattr(dis, 'regions', regions)

                # look for pleiotropy by looking for diseases for the markers in IC_STATS and other study hits
                stats_query = ElasticQuery.filtered(Query.terms("marker", all_markers),
                                                    Filter(RangeQuery("p_value", lte=5E-08)), sources=['marker'])
                stats_docs = Search(stats_query, idx=ElasticSettings.idx("IC_STATS"),
                                    size=len(all_markers)).search().docs

                other_hits_query = ElasticQuery(
                        BoolQuery(must_arr=[RangeQuery("tier", lte=2), Query.terms("marker", all_markers)]),
                        sources=['marker', 'disease'])
                other_hits = Search(other_hits_query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'),
                                    size=5000).search().docs

                for region in regions:
                    diseases = [dis_code]
                    for doc in stats_docs:
                        if getattr(doc, 'marker') in region['markers']:
                            meta_info = elastic_meta[doc.index()]['mappings'][doc.type()]['_meta']
                            if meta_info['disease'] not in diseases:
                                diseases.append(meta_info['disease'])

                    for doc in other_hits:
                        if getattr(doc, 'marker') in region['markers']:
                            if doc.disease is not None and doc.disease not in diseases:
                                diseases.append(doc.disease)
                    region['diseases'] = diseases

                studies = StudyDocument.get_studies(disease_code=dis_code)
                for doc in studies:
                    setattr(doc, 'study_id', getattr(doc, 'study_id').replace('GDXHsS00', ''))
                    pmid = getattr(doc, 'principal_paper')
                    pubs = PublicationDocument.get_publications(pmid, sources=['date', 'authors.name', 'journal'])
                    if len(pubs) > 0:
                        authors = getattr(pubs[0], 'authors')
                        setattr(doc, 'date', getattr(pubs[0], 'date'))
                        setattr(doc, 'journal', getattr(pubs[0], 'journal'))
                        setattr(doc, 'author', authors[0]['name'].rsplit(None, 1)[-1] if authors else "")
                setattr(dis, 'studies',  studies)

            context['features'] = disease_docs
            context['title'] = names
            return context
        raise Http404()
