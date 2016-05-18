''' Pydgin IGV Genome Browser settings '''
DEAFULT_GENOME = 'hg38'

''' Genomes available '''
GENOME_DETAILS = {
    'hg38': {
        'display_name': 'Human (GRCh38)',
        'locus': 'chr1:113,813,811-113,871,759',
        'tracks': {
            # 'genes': {'url': "/static/data/igv/hg38/gencode.v21.collapsed.bed"}
            'genes': {'url': "/static/data/igv/hg38/Homo_sapiens.GRCh38.83.bed"},
            'dbsnp': {'url': "/static/data/igv/hg38/dbsnp146-b38-All.vcf.gz"},
            # 'dbsnp': {'url': '//data.broadinstitute.org/igvdata/annotations/hg19/dbSnp/snp137.hg19.bed.gz'},
            'dbsnp_density1': {'url': "/static/data/igv/hg38/bed_chr_22.bed.wig"},
            'dbsnp_density2': {'url': "/static/data/igv/hg38/bed_chr_22.bed.2.wig"},
        }
    },
    'hg19': {
        'display_name': 'Human (GRCh37)',
        'locus': 'chr1:114,356,432-114,414,375',
        'tracks': {
            'genes': {'url': "/static/data/igv/hg19/Homo_sapiens.GRCh37.75.bed"}
        }
    },
#    'hg18': {
#        'display_name': 'Human (NCBI36)',
#        'locus': 'chr1:114,157,955-114,215,898',
#        'tracks': {
#            'genes': {'url': "//igv.broadinstitute.org/annotations/hg18/genes/gencode.v14.collapsed.bed"}
#        }
#    }
}

TRACK_DETAILS = {
    'genes': {
        'name': "Genes",
        'displayMode': "EXPANDED",
        'order': 1
    },
    'dbsnp': {
        'name': "Markers (dbSNP)",
        'displayMode': "COLLAPSED",
        'order': 2,
        'zoom_level': ':5000',
        'visibilityWindow': 5000
    },
    'dbsnp_density1': {
        'name': "dbSNP Density",
        'displayMode': "COLLAPSED",
        'order': 2,
        'zoom_level': '5000:200000'
    },
    'dbsnp_density2': {
        'name': "dbSNP Density",
        'displayMode': "COLLAPSED",
        'order': 2,
        'zoom_level': '200000:'
    },
    'ic_cro_liu': {
        'url': "/static/data/rs2476601.gwas",
        'name': "CRO - Liu",
        'featureType': "gwas",
        'format': 'gwasSNPS',
        'order': 100,
        'variantURL': "/marker/",
    }
}
