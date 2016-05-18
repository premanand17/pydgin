(function( ld, $, undefined ) {
	
	// get interaction details for interation section
	ld.run = function(m1, parameters, ld_result_id, maf, pos) {
    	// get the markers in LD
    	if(m1.length <3) {
			return;
		}
		maf = maf || false;
		pos = pos || false;

    	var url = "/rest/ld/?format=json";
	    $.ajax({
	    	type: "GET",
	    	url: url,
	    	data: parameters,
	    	success: function(jsonObj) {
				var tbl = '<table id="ld_table" class="display responsive table table-striped table-condensed"><thead>';
				tbl += "<th>marker</th><th>r<sup>2</sup></th><th>D'</th>";
				if(maf){
					tbl += '<th>MAF</th>';
				}
				if(pos){
					tbl += '<th>position</th>';
				}
				tbl += '</thead><tbody></tbody></table>';

				$("#"+ld_result_id).html(tbl);
				var ld_results = jsonObj[0]['ld'];
				if(ld_results === null) {
					return;
				}
				
				for(var i=0; i<ld_results.length; i++) {
					var ld = ld_results[i];
					var row = '<tr><td nowrap><a href="/marker/?m='+ ld['marker2'] +'">'+ ld['marker2'] +'</a></td>';
					row += '<td>'+ld['rsquared'].toFixed(2)+'</td>';
					row += '<td>'+ld['dprime'].toFixed(2)+'</td>';
					if($("input[name*='maf']").is(":checked")){
						row += '<td>'+ld['MAF']+'</td>';
					}
					if($("input[name*='pos']").is(":checked")){
						row += '<td>'+ld['position']+'</td>';
					}
					row += '</td></tr>';
					$('#ld_table tbody').append(row);
				}
				
				$('#ld_table').dataTable({
                    dom: 'Blfrtip',
                    "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
                    "buttons": ['copy', 'csv', 'excel', 'pdf', 'print'],
                    "order": [[ 1, "desc" ]]
                });
	    	},
	    	error: function(jqXHR, textStatus, errorThrown) {
	    		$("#"+ld_result_id).html('PROBLEM CONNECTING: '+errorThrown);
	    	}
	    	
	    });
	}



}( window.ld = window.ld || {}, jQuery ));
