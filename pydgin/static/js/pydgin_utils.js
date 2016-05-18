(function(pydgin_utils, $, undefined) {
	pydgin_utils.getCookie = function(name) {
	    var cookieValue = null;
	    if (document.cookie && document.cookie != '') {
	        var cookies = document.cookie.split(';');
	        for (var i = 0; i < cookies.length; i++) {
	            var cookie = jQuery.trim(cookies[i]);
	            // Does this cookie string begin with the name we want?
	            if (cookie.substring(0, name.length + 1) == (name + '=')) {
	                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                break;
	            }
	        }
	    }
	    return cookieValue;
	}

	// add a spinner before an html element
	pydgin_utils.add_spinner_before = function(parent_id, spinner_id) {
		$('#'+parent_id).before('<i id="'+spinner_id+'" class="fa fa-spinner fa-spin"></i>');
	}
	
	// escape colon and dot in element id
	pydgin_utils.escape_id = function(id) {
		 return id.replace( /(:|\.|\[|\])/g, "\\$1" );
	}
}( window.pydgin_utils = window.pydgin_utils || {}, jQuery ));

