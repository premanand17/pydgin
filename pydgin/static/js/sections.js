(function( sections, $, undefined ) {
    // retrieve publications for publications section
    sections.get_publication_details = function(opubid, pmids) {
    	var pubid = pydgin_utils.escape_id(opubid);
        $.ajax({
            type: "POST",
            url: "/gene/publications/",
            data: {'pmids': pmids},
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", pydgin_utils.getCookie('csrftoken'));
                }
            },
            success: function(hits, textStatus, jqXHR) {
                pydgin_utils.add_spinner_before(pubid, opubid+"-spinner");
                for(var i=0; i<hits.hits.length; i++) {
                    var hit = hits.hits[i]._source;
                    var row = '<tr><td nowrap><a href="http://www.ncbi.nlm.nih.gov/pubmed/'+ hit.pmid +'?dopt=abstract" target="_blank">'+ hit.pmid +'</a>';
                    row += ' <i class="fa fa-info-circle pmidinfo" data-toggle="popover" data-trigger="manual" data-poload="'+hit.pmid+'"></i></td>';
                    row += '<td class="visible-md visible-lg">'+ hit.title + '</td>';

                    if (hit.authors === undefined || hit.authors[0] === undefined) {
                        row += '<td class="visible-md visible-lg">n/a</td>';
                    } else {
                        row += '<td class="visible-md visible-lg">' + hit.authors[0].name + '</td>';
                    }
                    row += '<td>' + hit.journal + '</td>';
                    if(hit.tags.disease) {
                        var disease = hit.tags.disease;
                        var dis_buttons = '';
                        $.each(disease, function( index, dis ) {
                        	dis = dis.toUpperCase();
                        	dis_buttons += '<a class="btn btn-default btn-disease ' + dis +
                        				   ' data-toggle="tooltip" style="width:46px; padding:5px; margin: 0 2px 2px" data-placement="top" href="/disease/' +
                        				   dis+'/">' + dis+'</a>';
                        });
                        row += '<td>'+dis_buttons+'</td>';
                    } else {
                        row += '<td>N/A</td>';
                    }
                    row += '<td nowrap>' + hit.date + '</td></tr>';
                    $('#'+pubid+' tbody').append(row);
                }
                sections.add_pmid_popover('#'+pubid+' tbody');

                var paginate = true;
                if(hits.hits.length < 12)
                    paginate = false;
                $('#'+pubid).dataTable({
                    dom: 'Bfrtip',
                    "bPaginate": paginate,
                    "bInfo": paginate,
                    "aaSorting": [[ 5, "desc" ]],
                    "buttons": ['copy', 'csv', 'excel', 'pdf', 'print']
                });
                $("#"+pubid+"-spinner").remove();
            }
        });
    }
    
    sections.add_pmid_popover = function(selector) {
        $(selector).on('mouseenter', '*[data-poload]', function() {
            var e = $(this);
            if(e.data('bs.popover')) {  // check if content already retrieved
                $(e).popover('show');
            } else {
                $.ajax({
                    type: "POST", url: "/gene/publications/",
                    data: {'pmids': [e.data('poload')]},
                    beforeSend: function(xhr, settings) {
                        if (!this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", pydgin_utils.getCookie('csrftoken'));
                        }
                    },
                    success: function(hits, textStatus, jqXHR) {
                        var src = hits.hits[0]._source;
                        title =  '<strong>'+src.title+'</strong>'
                        pmid_html = '';
                        for(var i=0; i<src.authors.length && i<3; i++) {
                            pmid_html += (i > 0 ? ', ' : '')+src.authors[i].name;
                        }
                        if(src.authors.length > 3) {
                            pmid_html += '..., '+src.authors[src.authors.length-1].name;
                        }
                        pmid_html += '<br>PMID:'+src.pmid+', <i>'+src.journal+'</i>, '+src.date;
                        if ($(window).width() > 768) {
                            pmid_html += '</p><p><strong>Abstract</strong>: '+src.abstract+'</p>';
                        }
                        e.popover({
                            title: title,
                            content: pmid_html,
                            html: true,
                            template:'<div class="popover popover-wide" role="tooltip">'
                            +'<div class="arrow"></div><h3 class="popover-title"></h3>'
                            +'<div class="popover-content"></div></div>'}).popover('show');
    
                        $(e).on("mouseleave", function () {
                            $(e).popover('hide');
                        });
                    }
                });
            }
        }).on('mouseleave', '*[data-poload]', function() {
            $(this).popover('hide');
        });
    }
}( window.sections = window.sections || {}, jQuery ));
