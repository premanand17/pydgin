''' Pydgin project settings. '''
from collections import OrderedDict
DEFAULT_BUILD = 38

''' Sections for pages. '''
PAGE_SECTIONS = {
    'GeneView': OrderedDict([
        ('overview', {'show': True, 'collapse': False}),
        ('igvBrowser', {'show': True, 'collapse': False}),
        ('external links', True),
        ('criteria', True),
        ('study', True),
        ('publications', {'show': True}),
        ('interactions', True),
        ('gene sets', True),
        ('phenotype links', True)]),
    'MarkerView': OrderedDict([
        ('overview', {'show': True, 'collapse': False}),
    #    ('igvBrowser', {'show': True, 'collapse': False}),
        ('historical ids', True),
        ('criteria', True),
        ('functional information', True),
        ('study', True),
        ('populations', True),
        ('linkage disequilibrium statistics', True)]),
    'StudyView': OrderedDict([
        ('overview', {'show': True, 'collapse': False}),
        ('study association', True),
        ('criteria', True),
        ('publications', {'show': True})
        ]),
    'DiseaseView': OrderedDict([
        ('overview', True)]),
    'RegionView': OrderedDict([
        ('overview', {'show': True, 'collapse': False}),
        ('criteria', True),
    #    ('igvBrowser', {'show': True, 'collapse': False}),
        ('study', True),
        ('publications', {'show': True})])
}

TOOLS = {
    'browser': {'title': 'Genome Browser', 'link': '/browser/'},
    'ld_tool': {'title': 'Linkage Disequilibrium', 'link': '/marker/ld_tool/'},
}

CDN = {
    "JQUERY": "//code.jquery.com/jquery-2.2.0.min.js",
    "JQUERY_UI": "//code.jquery.com/ui/1.11.4/jquery-ui.js",
    "BOOTSTRAP": "//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.5/js/bootstrap.min.js",
    "QUNIT": "//code.jquery.com/qunit/qunit-1.21.0.js",
    "QUNIT_CSS": "//code.jquery.com/qunit/qunit-1.21.0.css",

    "DATATABLES": "//cdn.datatables.net/1.10.10/js/jquery.dataTables.min.js",
    "DATATABLES_RESPONSIVE": "//cdn.datatables.net/responsive/2.0.0/js/dataTables.responsive.min.js",
    "DATATABLES_BS": "//cdn.datatables.net/1.10.10/js/dataTables.bootstrap.min.js",

    # datatables exports
    "DATATABLES_BUTTONS": "//cdn.datatables.net/buttons/1.1.0/js/dataTables.buttons.min.js",
    "BUTTONS_FLASH": "//cdn.datatables.net/buttons/1.1.0/js/buttons.flash.min.js",
    "JSZIP": "//cdnjs.cloudflare.com/ajax/libs/jszip/2.5.0/jszip.min.js",
    "PDFFMAKE": "//cdn.rawgit.com/bpampuch/pdfmake/0.1.18/build/pdfmake.min.js",
    "VFS_FONTS": "//cdn.rawgit.com/bpampuch/pdfmake/0.1.18/build/vfs_fonts.js",
    "BUTTONS_HTML5": "//cdn.datatables.net/buttons/1.1.0/js/buttons.html5.min.js",
    "BUTTONS_PRINT": "//cdn.datatables.net/buttons/1.1.0/js/buttons.print.min.js",

    # form validation
    "FORM_VALIDATOR": "//cdnjs.cloudflare.com/ajax/libs/jquery-form-validator/2.2.8/jquery.form-validator.min.js",

    #
    # CSS
    #
    "JQUERY_UI_CSS": "//code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css",
    "FONT_AWSUM": "//maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css",

    "DATATABLES_BS_CSS": "//cdn.datatables.net/1.10.10/css/dataTables.bootstrap.min.css",
    "DATATABLES_RESPONSIVE_CSS": "//cdn.datatables.net/responsive/2.0.0/css/responsive.dataTables.min.css",
    "DATATABLES_BUTTONS_CSS": "//cdn.datatables.net/buttons/1.1.0/css/buttons.dataTables.min.css"
}
