/*
 * conet plugin for javascript over Jquery
 */

/*
 * globals
 */

var link="http://localhost:8080/io";

/*
 * ajax
 */
var ajaxResult=function(params,callback)
	{
		$.ajax({url:link,cache: false,dataType: 'text',
				success: function(html)
				{
					if(jQuery.isFunction(callback))
					{
						callback(html);
					}
				}
			  	
			  });
	}


var parseObj=function(params)
	{
		return jQuery.parseJSON(params);
	}


