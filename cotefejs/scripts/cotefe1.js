(function($){
	
	var cotefe = {
			baseurl:"http://localhost:8080",
			apiurl: "https://api.cotefe.net/",
			token : "1908700504b2474e9e9d6cc6225d3ece",
			
		};
	
	/*
	 * user model
	 */
	user = Backbone.Model.extend({url:cotefe.apiurl+"me"+"?access_token="+cotefe.token,	uri:"",	media_type:"",username:"",id: 31034,first: "",last: "",
					email: "",organization: "",	projects:[],experiemnts:[],	jobs: [],datetime_created: "",datetime_modified: "",
					display: function(item) {
					    this.fetch({
					      	success: function(model, response) {
					      			new ListView({el:item,model:model});
					        		return (model);
					      		}
				    		});
				  	},
				
	      });
	
	/*
	 * a resource model
	 */
	resource  = Backbone.Model.extend({
					display: function(item) {
					    this.fetch({
					      	success: function(model, response) {
					      		new ListView({el:item,model:model});
					        		return (model);
					      		}
				    		});
				  		}
		  });
	
	/*
	 * project list based on project model
	 */
	ResourceList = Backbone.Collection.extend({	model:resource,	display:function(item){	this.fetch({success: function(model,result) {new ListView({el:item,model:model});}})}, 
		 });
	
	projectList=ResourceList.extend({url:cotefe.apiurl+"projects/?access_token="+cotefe.token});
	experimentList=ResourceList.extend({url:cotefe.apiurl+"experiments/?access_token="+cotefe.token});
	jobList=ResourceList.extend({url:cotefe.apiurl+"jobs/?access_token="+cotefe.token});
	
	
	
	
	ListView=Backbone.View.extend({
		initialize:function(){_.bindAll(this,"render");this.render();},
		render:function()
		{
			$(this.el).val(JSON.stringify(this.model,null,'\t'));
		}
	});

})(jQuery)



$(document).ready(function(){
   
   usera= new user();   
   usera.display("#userContent");

   $('input[type=button]').click(function(){
   				element=$(this).parents('form');
   				type=(element.attr("class"));
   				method=$(this).attr('name');
   				
   				switch(method)
   				{
   					case 'GET':resourcetype(type);
   				
   				}
   				
   				
   				
   			});
   
   
	
	/*
	 * slide form DIV
	 */
	$("h3").on("click",function(){$(this).next("form").slideToggle("slow");});

   
 });


function resourcetype(type)
{
	switch(type)
	{
		case "project": prjs=new projectList();prjs.display("#projects");break;
		case "experiment":experiments=new experimentList();experiments.display("#experiments");break;
		case "job":jobs=new jobList();jobs.display("#jobs");break;
	
	}
	
}
