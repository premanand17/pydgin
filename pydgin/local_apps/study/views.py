''' Study views. '''
from django.contrib import messages
from django.http import Http404
from django.http.response import JsonResponse
from django.views.generic.base import TemplateView, View

from core.views import SectionMixin
from criteria.helper.study_criteria import StudyCriteria
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query, Filter
from elastic.search import ElasticQuery, Search
from gene import utils
from study.document import StudyDocument
from disease.utils import Disease
from region.document import DiseaseLocusDocument, RegionDocument,\
    StudyHitDocument
from core.document import PublicationDocument
from elastic.result import Document


class StudyView(SectionMixin, TemplateView):
    ''' Renders a study page. '''
    template_name = "study/index.html"

    def get_context_data(self, **kwargs):
        context = super(StudyView, self).get_context_data(**kwargs)
        study = kwargs['study'] if 'study' in kwargs else self.request.GET.get('s')
        return StudyView.get_study(self.request, study, context)

    @classmethod
    def get_study(cls, request, study, context):
        if study is None:
            messages.error(request, 'No study id given.')
            raise Http404()

        studies = StudyDocument.get_studies(study_ids=study.split(','), split_name=False)

        if len(studies) == 0:
            messages.error(request, 'Study(s) '+study+' not found.')
        elif len(studies) < 9:
            names = ', '.join([getattr(doc, 'study_name') for doc in studies])
            context['features'] = studies

            fids = [doc.doc_id() for doc in studies]
            criteria_disease_tags = StudyView.criteria_disease_tags(request, fids)
            context['criteria'] = criteria_disease_tags
            context['title'] = names
            for doc in studies:
                setattr(doc, 'study_name', getattr(doc, 'study_name').split(':', 1)[0])
                pubs = PublicationDocument.get_publications(getattr(doc, 'principal_paper'),
                                                            sources=['date', 'title'])
                if len(pubs) > 0:
                    setattr(doc, 'principal_publication', pubs[0])

                if getattr(doc, 'sub_studies'):
                    assoc_studies = StudyDocument.get_studies(study_ids=getattr(doc, 'sub_studies'),
                                                              sources=['study_id', 'principal_paper'])
                    for assoc_study in assoc_studies:
                        pubs = PublicationDocument.get_publications(getattr(assoc_study, 'principal_paper'),
                                                                    sources=['date', 'title'])
                        if len(pubs) > 0:
                            setattr(assoc_study, 'principal_publication', pubs[0])
                    setattr(doc, 'assoc_studies', assoc_studies)

                hits = RegionDocument.get_hits_by_study_id(doc.doc_id(),
                                                           sources=['chr_band', 'genes', 'marker', 'alleles', 'pmid',
                                                                    'build_info', 'disease_locus', 'p_values',
                                                                    'odds_ratios', 'dil_study_id'])
                StudyHitDocument.process_hits(hits, None)
                setattr(doc, 'hits', Document.sorted_alphanum(hits, 'chr_band'))
            return context
        raise Http404()

    @classmethod
    def criteria_disease_tags(cls, request, qids):
        ''' Get criteria disease tags for a given study ID for all criterias. '''
        criteria_disease_tags = StudyCriteria.get_all_criteria_disease_tags(qids)
        return criteria_disease_tags


def criteria_details(request):
    ''' Get criteria details for a given study ID. '''
    study_id = request.POST.get('feature_id')
    criteria_details = StudyCriteria.get_criteria_details(study_id)
    return JsonResponse(criteria_details)


class StudiesEntryView(TemplateView):
    ''' Entry point page for studies and disease region tables. '''
    template_name = "study/studies_regions_entry.html"

    def get_context_data(self, **kwargs):
        context = super(StudiesEntryView, self).get_context_data(**kwargs)
        studies = StudyDocument.get_studies(sources=['study_id', 'study_name', 'diseases',
                                                     'principal_paper', 'authors'])
        for doc in studies:
            setattr(doc, 'study_id', getattr(doc, 'study_id').replace('GDXHsS00', ''))
            pmid = getattr(doc, 'principal_paper')
            pubs = PublicationDocument.get_publications(pmid, sources=['date'])
            if len(pubs) > 0:
                setattr(doc, 'date', getattr(pubs[0], 'date'))

        context['studies'] = studies
        (core, other) = Disease.get_site_diseases()
        diseases = list(core)
        diseases.extend(other)
        context['diseases'] = diseases

        for dis in diseases:
            docs = DiseaseLocusDocument.get_disease_loci_docs(getattr(dis, 'code'))
            # get visible/authenticated hits id's
            visible_hits = DiseaseLocusDocument.get_hits([h for r in docs for h in getattr(r, 'hits')],
                                                         sources=['seqid'])
            visible_hits_ids = [h.doc_id() for h in visible_hits]
            regions = 0
            for r in docs:
                hits = getattr(r, 'hits')
                for h in hits:
                    if h in visible_hits_ids:
                        regions += 1
                        break
            # number of visible regions
            setattr(dis, 'count', regions)

        return context


class StudySectionView(View):
    ''' Study section for gene/marker/region. '''

    def post(self, request, *args, **kwargs):
        ens_id = self.request.POST.get('ens_id')
        marker = self.request.POST.get('marker')
        markers = self.request.POST.getlist('markers[]')

        if ens_id:
            sfilter = Filter(Query.query_string(ens_id, fields=["genes"]).query_wrap())
        elif marker:
            sfilter = Filter(Query.query_string(marker, fields=["marker"]).query_wrap())
        elif markers:
            sfilter = Filter(Query.query_string(' '.join(markers), fields=["marker"]).query_wrap())

        query = ElasticQuery.filtered(Query.match_all(), sfilter)
        elastic = Search(query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'), size=500)
        study_hits = elastic.get_json_response()['hits']

        ens_ids = []
        pmids = []
        for hit in study_hits['hits']:
            if 'pmid' in hit['_source']:
                pmids.append(hit['_source']['pmid'])
            if 'genes' in hit['_source']:
                for ens_id in hit['_source']['genes']:
                    ens_ids.append(ens_id)
        docs = utils.get_gene_docs_by_ensembl_id(ens_ids, ['symbol'])
        pub_docs = PublicationDocument.get_pub_docs_by_pmid(pmids, sources=['authors.name', 'journal'])

        for hit in study_hits['hits']:
            genes = {}
            if 'genes' in hit['_source']:
                for ens_id in hit['_source']['genes']:
                    try:
                        genes[ens_id] = getattr(docs[ens_id], 'symbol')
                    except KeyError:
                        genes = {ens_id: ens_id}
            hit['_source']['genes'] = genes
            if 'pmid' in hit['_source']:
                pmid = hit['_source']['pmid']
                try:
                    authors = getattr(pub_docs[pmid], 'authors')
                    journal = getattr(pub_docs[pmid], 'journal')
                    hit['_source']['pmid'] = \
                        {'pmid': pmid,
                         'author': authors[0]['name'].rsplit(None, 1)[-1] if authors else "",
                         'journal': journal}
                except KeyError:
                    hit['_source']['pmid'] = {'pmid': pmid}

        return JsonResponse(study_hits)
