''' Template tags for the marker app. '''
import logging

from django import template

from elastic.elastic_settings import ElasticSettings
from elastic.query import BoolQuery, Filter, Query
from elastic.search import Search, ElasticQuery
from collections import OrderedDict


register = template.Library()

logger = logging.getLogger(__name__)


@register.filter
def gene_info(marker_doc):
    ''' Retrieve gene(s) information from the INFO column. '''
    if hasattr(marker_doc, 'info'):
        info = getattr(marker_doc, 'info')
        info_parts = dict(item.split("=", 1) for item in info.split(";") if '=' in item)
        if 'GENEINFO' not in info_parts:
            return None
        try:
            sym = [g.split(':')[0].lower() for g in info_parts['GENEINFO'].split('|')]

            equery = BoolQuery(b_filter=Filter(Query.terms('symbol', sym)))
            search_query = ElasticQuery(equery, sources=['symbol'])
            (idx, idx_type) = ElasticSettings.idx('GENE', 'GENE').split('/')
            docs = Search(search_query=search_query, size=len(sym), idx=idx, idx_type=idx_type).search().docs
            return {getattr(doc, 'symbol'): doc.doc_id() for doc in docs}
        except Exception as e:
            logger.error(e.message)
    return None


@register.filter
def marker_functional_info(marker_doc):
    ''' Retrieve functional information from bitfield in the INFO column.
    ftp://ftp.ncbi.nlm.nih.gov/snp/specs/dbSNP_BitField_latest.pdf
    '''
    if hasattr(marker_doc, 'info'):
        info = getattr(marker_doc, 'info')
        info_parts = dict(item.split("=", 1) for item in info.split(";") if '=' in item)
        if 'VP' not in info_parts:
            return None
        vp = info_parts['VP']

        if vp.startswith('0x'):
            vp = vp[2:]

        h_size = len(vp) * 4
        info_bits = (bin(int(vp, 16))[2:]).zfill(h_size)
        F2_1 = info_bits[24:32]     # gene function properties
        F2_2 = info_bits[32:40]

        # F0 = bin(int(vp[0:2], 16))[2:].rjust(8, '0')     # version encoding
        # F1_1 = bin(int(vp[2:4], 16))[2:].rjust(8, '0')   # resource link properties
        # F1_2 = bin(int(vp[4:6], 16))[2:].rjust(8, '0')
        # F2_1 = bin(int(vp[6:8], 16))[2:].rjust(8, '0')     # gene function properties
        # F2_2 = bin(int(vp[8:10], 16))[2:].rjust(8, '0')
        # F3 = bin(int(vp[10:12], 16))[2:].rjust(8, '0')   # mapping
        # F4 = bin(int(vp[12:14], 16))[2:].rjust(8, '0')   # allele frequency
        # F5 = bin(int(vp[14:16], 16))[2:].rjust(8, '0')   # genotype
        # F6 = bin(int(vp[16:18], 16))[2:].rjust(8, '0')   # validation by HapMap/TGP
        # F7 = bin(int(vp[18:20], 16))[2:].rjust(8, '0')   # phenotype
        # F8 = bin(int(vp[20:22], 16))[2:].rjust(8, '0')   # variation class
        # F9 = bin(int(vp[22:24], 16))[2:].rjust(8, '0')   # quality check

        functional_f2 = OrderedDict([
            ('in gene seg', F2_1[7] == '1'),
            ('in 5prime gene region', F2_1[6] == '1'),
            ('in 3prime gene region', F2_1[5] == '1'),
            ('in intron', F2_1[4] == '1'),
            ('in donor splice site', F2_1[3] == '1'),
            ('in acceptor_splice_site', F2_1[2] == '1'),
            ('in 5prime utr', F2_1[1] == '1'),
            ('in 3prime utr', F2_1[0] == '1'),

            ('has synonymous', F2_2[7] == '1'),
            ('has reference', F2_2[6] == '1'),
            ('has stop gain', F2_2[5] == '1'),
            ('has non-synonymous missense', F2_2[4] == '1'),
            ('has non-synonymous frameshift', F2_2[3] == '1'),
            ('has stop loss', F2_2[2] == '1')
        ])

        return functional_f2
    return None
