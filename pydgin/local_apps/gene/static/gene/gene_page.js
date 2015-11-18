(function( gene_page, $, undefined ) {
	// retrieve publications for publications section
	gene_page.get_publication_details = function(pubid, pmids) {
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
				pydgin_utils.add_spinner_before(pubid, pubid+"-spinner");
				for(var i=0; i<hits.hits.length; i++) {
        			var hit = hits.hits[i]._source;
        			var row = '<tr><td nowrap><a href="http://www.ncbi.nlm.nih.gov/pubmed/'+ hit.pmid +'?dopt=abstract" target="_blank">'+ hit.pmid +'</a>';
        			row += ' <i class="fa fa-info-circle pmidinfo" data-toggle="popover" data-trigger="manual" data-poload="'+hit.pmid+'"></i></td>';
        			row += '<td class="visible-md visible-lg">'+ hit.title + '</td>';

        			if (hit.authors[0] === undefined) {
        				row += '<td class="visible-md visible-lg">n/a</td>';
        			} else {
        				row += '<td class="visible-md visible-lg">' + hit.authors[0].name + '</td>';
        			}
        			row += '<td>' + hit.journal + '</td>';
        			if(hit.tags.disease) {
        				var disease = hit.tags.disease;
        				var diseaseArray = $.map(disease, function(item, index) {
        				    return item.toUpperCase();
        				});
        				row += '<td>' + diseaseArray + '</td>';
        			} else {
        				row += '<td>N/A</td>';
        			}
        			row += '<td nowrap>' + hit.date + '</td></tr>';
        			$('#'+pubid+' tbody').append(row);
				}
				add_pmid_popover('#'+pubid+' tbody');

				var paginate = true;
				if(hits.hits.length < 12)
					paginate = false;
				$('#'+pubid).dataTable({
					"bPaginate": paginate,
					"bInfo": paginate,
			        "aaSorting": [[ 5, "desc" ]]
			    });
				$("#"+pubid+"-spinner").remove();
			}
		});
	}
	
	// get interaction details for interation section
	gene_page.get_interaction_details = function(ens_id) {
		$.ajax({
			type: "POST",
			url: "/gene/interactions/",
			data: {'ens_id': ens_id},
		    beforeSend: function(xhr, settings) {
		        if (!this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", pydgin_utils.getCookie('csrftoken'));
		        }
		    },
			success: function(hits, textStatus, jqXHR) {
				pydgin_utils.add_spinner_before('table-interactor-'+ens_id, "interactor-spinner-"+ens_id);
				for(var i=0; i<hits.hits.length; i++) {
        			var hit = hits.hits[i]._source;
        			var row =  "";
        			for(var j=0; j<hit.interactors.length; j++) {
        				row += '<tr><td><a href="/gene/?g=' + hit.interactors[j].interactor + '">'+hit.interactors[j].symbol+'</a></td>';
        				if(hit.interactors[j].pubmed) {
	        				row += '<td><a href="http://www.ncbi.nlm.nih.gov/pubmed/' + 
	        				         hit.interactors[j].pubmed + '?dopt=abstract" target="_blank">'+
	        				         hit.interactors[j].pubmed+'</a>';
	        				row += ' <i class="fa fa-info-circle pmidinfo" data-toggle="popover" data-trigger="manual" data-poload="'+hit.interactors[j].pubmed+'"></i></td>';
	        				row += '</td>';
        				} else {
        					row += '<td></td>';
        				}
        				row += '<td>' + hit.interaction_source + '</td></tr>';
        			}
        			$('#table-interactor-'+ens_id+' tbody').append(row);
				}
				add_pmid_popover('#table-interactor-'+ens_id);
				$('#table-interactor-'+ens_id).DataTable();
				$("#interactor-spinner-"+ens_id).remove();
			}
		});
	}

	// get gene sets for pathway gene sets section
	gene_page.get_genesets_details = function(ens_id) {
		$.ajax({
			type: "POST",
			url: "/gene/genesets/",
			data: {'ens_id': ens_id},
		    beforeSend: function(xhr, settings) {
		        if (!this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", pydgin_utils.getCookie('csrftoken'));
		        }
		    },
			success: function(hits, textStatus, jqXHR) {
				pydgin_utils.add_spinner_before('table-genesets-'+ens_id, "gs-spinner-"+ens_id);
				for(var i=0; i<hits.hits.length; i++) {
        			var hit = hits.hits[i]._source;
        			var ngenes = Object.keys(hit.gene_sets).length;
        			var row = '<tr><td><a href="' + hit.pathway_url + '" target="_blank">'+
        			          hit.pathway_name.replace(/_/g, ' ')+'</a> (';
        			var genes = add_genes(hit.pathway_name, ens_id, hit.gene_sets);
        			row += ngenes+')<td>'+genes+'</td></tr>';
         			$('#table-genesets-'+ens_id+' tbody').append(row);
				}
				$('#table-genesets-'+ens_id).DataTable();
				$("#gs-spinner-"+ens_id).remove();
			}
		});
	}
	
	// get gene sets for pathway gene sets section
	gene_page.get_study_details = function(ens_id) {
		$.ajax({
			type: "POST",
			url: "/gene/studies/",
			data: {'ens_id': ens_id},
		    beforeSend: function(xhr, settings) {
		        if (!this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", pydgin_utils.getCookie('csrftoken'));
		        }
		    },
			success: function(hits, textStatus, jqXHR) {
				pydgin_utils.add_spinner_before('table-study-'+ens_id, "study-spinner-"+ens_id);
				for(var i=0; i<hits.hits.length; i++) {
        			var hit = hits.hits[i]._source;
        			var row = '<tr><td>'+hit.dil_study_id.replace('GDXHsS00', '')+'</td>';
        			row +='<td>'+add_pub(hit.pmid)+'</td>';
        			row +='<td>'+hit.disease+'</td>';
        			row +='<td>'+hit.chr_band;
        			if(hit.notes !== null) {
        				row += ' <a name="'+hit.dil_study_id+'" class="popoverData" data-placement="top" href="#" rel="popover" data-trigger="manual">&dagger;</a>';
        				row += '<div id="popover-content-'+hit.dil_study_id+'" class="hide">'+hit.notes+'</div>';
        			}
        			row += '</td>';
        			row +='<td><a href="/marker/?m='+hit.marker+'">'+hit.marker+'</a></td>';

        			var or = hit.odds_ratios.combined.or;
        			if(or === null) {
        				or = hit.odds_ratios.discovery.or;
        				if(or === null) {
        					or = "";
        				}
        			}

        			row +='<td><span class="label '+(or < 1 ? 'label-primary': 'label-danger')+'">'+hit.alleles.major+'>'+hit.alleles.minor+'</span></td>';
        			var pval = hit.p_values.combined;
        			row +='<td class="visible-md visible-lg" nowrap>'+parseFloat((pval !== null? pval : hit.p_values.discovery)).toExponential()+'</td>';
        			row +='<td class="visible-md visible-lg">'+or+'</td>';
        			row +='<td class="visible-md visible-lg">'+(hit.alleles.maf !== null ? hit.alleles.maf : "")+'</td>';
        			row +='<td class="visible-md visible-lg">';
        			row += add_genes(hit.dil_study_id, ens_id, hit.genes);
        			row +='</td>';
        			row += '</tr>';
         			$('#table-study-'+ens_id+' tbody').append(row);
				}
				$('#table-study-'+ens_id+' .popoverData').popover({ 
				    html : true,
				    content: function() {
				      return $("#popover-content-"+$(this).attr('name')).html();
				    }
				});
				add_pmid_popover('#table-study-'+ens_id);
				var paginate = true;
				if(hits.hits.length < 12)
					paginate = false;
				$('#table-study-'+ens_id).dataTable({
					"bPaginate": paginate,
					"bInfo": paginate,
					"aoColumns": [null,
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false}],
			        "aaSorting": [[ 0, "asc" ]]
			    });
				$("#study-spinner-"+ens_id).remove();
			}
		});
	}
	
	add_pub = function(pub) {
		var row ='<a href="http://www.ncbi.nlm.nih.gov/pubmed/'+pub.pmid+'?dopt=abstract" target="_blank">';
		if ($(window).width() > 768) {
			row += (pub.author ? pub.author : pub.pmid) + ' ' + (pub.journal ? '(<i>'+pub.journal+'</i>)' : '');
			row += '</a> ';
			row += '<i class="fa fa-info-circle pmidinfo" data-toggle="popover" data-trigger="manual" data-poload="'+pub.pmid+'"></i>';
		} else {
			row += (pub.author ? pub.author : pub.pmid) + '</a> ';
		}
		return row;
	}

	add_genes = function(hit_name, ens_id, genes) {
		var count = 0;
		var row = "";
		$.each(genes, function(key,value) {
			if(count == 14) {
				var more_id = hit_name+'_more';
				row += 
'<a role="button" data-toggle="collapse" href="#'+more_id+'" aria-expanded="false" aria-controls="mappingFilters">'+
' <i class="fa fa-caret-square-o-down"></i></a>';
				row += '<div class="collapse" id="'+more_id+'">';
			} else if(count > 0) {
				row += ', ';
			}
			row += (key !== ens_id ? '<a href="/gene/?g='+key+'">'+value+"</a>" : value)
			count++;
		});
		return row;
	}

	add_pmid_popover = function(selector) {
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
}( window.gene_page = window.gene_page || {}, jQuery ));
