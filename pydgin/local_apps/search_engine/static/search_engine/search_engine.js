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
}( window.search_engine = window.search_engine || {}, jQuery ));
