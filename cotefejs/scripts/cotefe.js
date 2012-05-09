(function($){
	
	var cotefe = {
			baseurl:"http://localhost:8080",
			apiurl: "https://api.cotefe.net/",
			token : "1908700504b2474e9e9d6cc6225d3ece",
			
		};
	
	
	Resource  = Backbone.Model.extend({
					display: function(item) {
					    this.fetch({
					      	success: function(model, response) {
					      		new ListView({el:item,model:model});
					        		return (model);
					      		}
				    		});
				  		}
		  });
	
	
	
	ResourceList = Backbone.Collection.extend({	model:Resource,	display:function(item){	this.fetch({success: function(model,result) {new ListView({el:item,model:model});}})},
		 });
	
	
	User=Resource.extend({url:cotefe.apiurl+"me"+"?access_token="+cotefe.token});						//user
	
	ProjectList=ResourceList.extend({url:cotefe.apiurl+"projects/?access_token="+cotefe.token});		//projects list
	ExperimentList=ResourceList.extend({url:cotefe.apiurl+"experiments/?access_token="+cotefe.token});	//experiment list
	JobList=ResourceList.extend({url:cotefe.apiurl+"jobs/?access_token="+cotefe.token});				//jobs list
	
	
	
	/*
	 * view
	 */
	
	ListView=Backbone.View.extend({
		initialize:function(){_.bindAll(this,"render");this.render();},
		render:function()
		{
			$(this.el).val(JSON.stringify(this.model,null,'\t'));
		}
	});
	
	
	
	
	/*
	 * help functions
	 */
	
	postModel=function(type)
	{
		url="";
		name=type+Math.floor(Math.random()*100);
		description=name+" Description";
		switch(type)
		{
			case "project":url=cotefe.apiurl+"projects/?access_token="+cotefe.token; break;
			case "experiment":url=cotefe.apiurl+"experiments/?access_token="+cotefe.token; break;
			case "job":url=cotefe.apiurl+"jobs/?access_token="+cotefe.token; break;
		}
		
		resource=new Resource({name:name,description:description});
		resource.url=url;
		resource.save({success:function(){alert("Successfully saved");}});
		
		
	}
	
	
	resourcetype = function(type)
	{
		switch(type)
		{
			case "project": prjs=new ProjectList();prjs.display("#projects");break;
			case "experiment":experiments=new ExperimentList();experiments.display("#experiments");break;
			case "job":jobs=new JobList();jobs.display("#jobs");break;		
		}
		
	}

	resourceSingleItem = function (id,type)
	{
		id=id.trim();
		switch(type)
		{
			case "project": 	single_project=new Resource();
	        					single_project.url=cotefe.apiurl+"projects/"+id+"?access_token="+cotefe.token;
	        					single_project.display("#projects");
	        					break;
			case "experiment":	single_exp=new Resource();
								single_exp.url=cotefe.apiurl+"experiments/"+id+"?access_token="+cotefe.token;
								single_exp.display("#experiments");
								break;
			case "job":jobs=	single_job=new Resource();
								single_job.url=cotefe.apiurl+"jobs/"+id+"?access_token="+cotefe.token;
								single_job.display("#jobs");
								break;
		
		}
		
	}
	
	removeSingleItem = function (id,type)
	{
		id=id.trim();
		resource=new Resource();;
		switch(type)
		{
			case "project": 	resource.url=cotefe.apiurl+"projects/"+id+"?access_token="+cotefe.token;
	        					break;
			case "experiment":	resource.url=cotefe.apiurl+"experiments/"+id+"?access_token="+cotefe.token;
								break;
			case "job":jobs=	resource.url=cotefe.apiurl+"jobs/"+id+"?access_token="+cotefe.token;
								break;
		
		}
		
		resource.destroy({success:function(){alert("Successfully Deleted");}});
		
	}


	checkInput = function(element)
	{
		text=$(element).next('input[type=text]').val();
		if(text.trim()!="")
			{
				return text;
			}
		return false;
	}
	
	

})(jQuery)



$(document).ready(function(){
   
   usera= new User();   
   usera.display("#userContent");

   $('input[type=button]').click(function(){
   				element=$(this).parents('form');
   				type=(element.attr("class"));
   				method=$(this).attr('name');
   				
   				switch(method)
   				{
   					case 'GET':	checkInput(this)!=false?resourceSingleItem(checkInput(this),type):resourcetype(type);break;
   					case 'POST': postModel(type);break;
   					case 'DELETE':checkInput(this)!=false?removeSingleItem(checkInput(this),type):alert("NO ID provided");break;
   				
   				}
   				
   				
   				
   			});
   
   
	
	/*
	 * slide form DIV
	 */
	$("h3").on("click",function(){$(this).next("form").slideToggle("slow");});

   
 });



