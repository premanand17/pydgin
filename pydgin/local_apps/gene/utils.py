from elastic.elastic_settings import ElasticSettings
from elastic.query import Query
from elastic.search import ElasticQuery, ScanAndScroll
from gene.document import GeneDocument


def get_gene_docs_by_ensembl_id(ens_ids, sources=None):
    ''' Get the gene symbols for the corresponding array of ensembl IDs.
    A dictionary is returned with the key being the ensembl ID and the
    value the gene document. '''
    genes = {}

    def get_genes(resp_json):
        hits = resp_json['hits']['hits']
        for hit in hits:
            genes[hit['_id']] = GeneDocument(hit)
    query = ElasticQuery(Query.ids(ens_ids), sources=sources)
    ScanAndScroll.scan_and_scroll(ElasticSettings.idx('GENE'), call_fun=get_genes, query=query)
    return genes
