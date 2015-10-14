(function( search_engine, $, undefined ) { 

	// auto-completion for search engine
	search_engine.autocomplete = function (searchId) {
		$( "#" + searchId ).autocomplete({
	        source: function( request, response ) {
	          $.ajax({
	            url: "/search/suggest",
	            contentType: 'application/json',
	            data: {
	              term: request.term,
	              idx: $( "#idx" ).val(),
	            },
	            success: function( data ) {
	              response( data.data );
	            }
	          });
	        },
	        minLength: 2,
	        open: function() {
	          $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
	        },
	        close: function() {
	          $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
	        },
	        select: function(event, ui) {
		       $( "#" + searchId ).val(ui.item.label);
		       $('#searchForm').submit();
		    }
	      });
	}

	// show / hide biotype panel
	search_engine.toggle_biotype = function (cat) {
	    if(cat === 'gene') {
	    	$('#biotypes').show();
	    } else {
	    	$('#biotypes').hide();
	    }
	}
	
	// show / hide category filters and biotype
	search_engine.toggle_category = function (active_cat) {
		$('#categories > li').each(function( index ) {
			 var cat = $( this ).attr('id');
			 $('#'+cat.replace("bucket", "filter")).hide();
		 });
		 search_engine.toggle_biotype(active_cat);
		 $('#filter-'+active_cat).show();
	};
}( window.search_engine = window.search_engine || {}, jQuery ));
