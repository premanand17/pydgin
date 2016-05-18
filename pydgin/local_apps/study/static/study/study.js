
(function( study, $, undefined ) {
	
	// get gene sets for pathway gene sets section
	study.get_study_details = function(ens_id, marker, markers) {
		$.ajax({
			type: "POST",
			url: "/study/section/",
			data: {'ens_id': ens_id, 'marker': marker, 'markers': markers},
		    beforeSend: function(xhr, settings) {
		        if (!this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", pydgin_utils.getCookie('csrftoken'));
		        }
		    },
			success: function(hits, textStatus, jqXHR) {
				var fid;
				if(ens_id) {
					fid = ens_id;
				} else if(marker) {
					fid = marker;
				} else {
					fid = '';
				}
				pydgin_utils.add_spinner_before('table-study-'+ens_id, "study-spinner-"+fid);
				for(var i=0; i<hits.hits.length; i++) {
        			var hit = hits.hits[i]._source;
        			var row = '<tr><td><a href="/study/'+hit.dil_study_id+'/">'+hit.dil_study_id.replace('GDXHsS00', '')+'</a></td>';
        			row +='<td>'+add_pub(hit.pmid)+'</td>';
        			row +='<td class="disease-bar" style="font-size:0.8em"><a class="btn btn-default btn-disease '+hit.disease+' data-toggle="tooltip" data-placement="top" href="/disease/'+hit.disease+'/">'+hit.disease+'</a></td>';
        			if(hit.disease_locus === 'TBC') {
        				row +='<td>'+hit.chr_band;
        			} else {
        				row +='<td><a href="/region/'+hit.disease_locus+'/">'+hit.chr_band+'</a>';
        			}
        			if(hit.notes !== null) {
        				row += ' <a name="'+hit.dil_study_id+'" class="popoverData" data-placement="top" href="#" rel="popover" data-trigger="hover">&dagger;</a>';
        				row += '<div id="popover-content-'+hit.dil_study_id+'" class="hide">'+hit.notes+'</div>';
        			}
        			row += '</td>';
        			row +='<td><a href="/marker/'+hit.marker+'/">'+hit.published_marker+'</a></td>';

        			var or = hit.odds_ratios.combined.or;
        			if(or === null) {
        				or = hit.odds_ratios.discovery.or;
        				if(or === null) {
        					or = "";
        				}
        			}

        			if(or === "") {
        				row +='<td>'+hit.alleles.major+'&gt;'+hit.alleles.minor+'</td>';
        			} else {
        				row +='<td><span class="label '+(or < 1 ? 'label-primary': 'label-danger')+'">'+hit.alleles.major+'&gt;'+hit.alleles.minor+'</span></td>';
        			}
        			var pval = hit.p_values.combined;
        			row +='<td class="visible-md visible-lg" nowrap>'+parseFloat((pval !== null? pval : hit.p_values.discovery)).toExponential()+'</td>';
        			row +='<td class="visible-md visible-lg">'+or+'</td>';
        			row +='<td class="visible-md visible-lg">'+(hit.alleles.maf !== null ? hit.alleles.maf : "")+'</td>';
        			row +='<td class="visible-md visible-lg">';
        			row += add_genes(hit.dil_study_id, ens_id, hit.genes);
        			row +='</td>';
        			row += '</tr>';
         			$('#table-study-'+fid+' tbody').append(row);
				}
				$('#table-study-'+fid+' .popoverData').popover({ 
				    html : true,
				    content: function() {
				      return $("#popover-content-"+$(this).attr('name')).html();
				    }
				});
				sections.add_pmid_popover('#table-study-'+fid);
				var paginate = true;
				if(hits.hits.length < 12)
					paginate = false;
				$('#table-study-'+fid).dataTable({
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
			        "aaSorting": [[ 0, "asc" ]],
			        'dom': 'Bfrtip',
			        "buttons": ['copy', 'csv', 'excel', 'pdf', 'print']
			    });
				$("#study-spinner-"+fid).remove();
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

}( window.study = window.study || {}, jQuery ));
