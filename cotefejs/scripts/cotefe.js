(function($) {

/*
 * cotefe constants
 */
	var cotefe = {
			baseurl:"http://localhost:8080",
			apiurl: "https://api.cotefe.net/",
			token : "1908700504b2474e9e9d6cc6225d3ece",
			
		};

	user = Backbone.Model.extend({
			//id:"https://api.cotefe.net/me?access_token=1908700504b2474e9e9d6cc6225d3ece",
			url:cotefe.apiurl+"me"+"?access_token="+cotefe.token,
	 		display: function() {
		    this.fetch({
		      	success: function(model, response) {
		        		console.log(response);
		        		console.log("***************************");
		        		console.log(JSON.stringify(model));
		        		//console.log(model.parse(response));
		      		}
	    		});
	  		}
	});

	project= Backbone.Model.extend({
		url:cotefe.apiurl+"projects/?access_token="+cotefe.token,
		display: function() {
		    	this.fetch({
		      		success: function(model, response) {
		        			//console.log(response);
		        			console.log("***************************");
		        			console.log(JSON.stringify(model));
		        			projectsview=new projectsview({model:model});
		        			projectsview.render();
		      			}
	    			});
	  			}	
		
	});
	
	projectsview= Backbone.View.extend({
		el:"#projects",
		render:function(eventname)
			{
				$(this.el).append(JSON.stringify(this.model));
			}
		
	});
	
	/*
	 * event for 
	 */
	clickOp= function()
	{
		$(".get").click(function(event){alert(event)});
	}
	
})(jQuery);

$(document).ready(function(){
   //model = new Model({label:'Test label'});
   //view = new ListAll({model: model});
   
   
   res= new user();
   res.display();
   clickOp();
   projects= new project();
   projects.display();
  
   
	
	
	/*
	 * slide form divs
	 */
	$("h3").click(function(){$(this).next("form").slideToggle("slow");});

   
 });



/*
//////test
Model = Backbone.Model.extend();
ListAll= Backbone.View.extend({
	el : '#test' ,
	initialize : function() {  _.bindAll(this, "render");this.render(); },
	render : function() 
	{
    		$(this.el).append( _.template('bla bla',this.model.toJSON()));
    		return this;
  	}
  	
});

/////// testing place
*/