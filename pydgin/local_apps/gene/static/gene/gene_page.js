(function( gene_page, $, undefined ) {
	
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
				sections.add_pmid_popover('#table-interactor-'+ens_id);
				$('#table-interactor-'+ens_id).DataTable({'dom': 'Bfrtip',"buttons": ['copy', 'csv', 'excel', 'pdf', 'print']});
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
				$('#table-genesets-'+ens_id).DataTable({'dom': 'Bfrtip',"buttons": ['copy', 'csv', 'excel', 'pdf', 'print']});
				$("#gs-spinner-"+ens_id).remove();
			}
		});
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

}( window.gene_page = window.gene_page || {}, jQuery ));
