
/*
 * cotefe JS -completely JS and client based
 */

(function($){
	
	/*
	 * initials
	 */
	var cotefe = {
			baseurl:"http://localhost:8080",
			apiurl: "http://192.168.103.114:8080/",//"https://api.cotefe.net/"
			token : "b53538ec924f40f1a0777aa996fec928",//1908700504b2474e9e9d6cc6225d3ece
			requesturl:"http://192.168.103.114:8080/oauth2/auth?client_id=a9db080f68f642fda61307323d035d28&redirect_uri=http://localhost:8080"
		};
	
	/*
	 * resource gives the model in return and fetches the URL
	 */
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
	
	
	/*
	 * get resource of collections
	 */
	
	ResourceList = Backbone.Collection.extend({	model:Resource,	display:function(item){	this.fetch({success: function(model,result) {new ListView({el:item,model:model});}})},
		 });
	
	
	User=Resource.extend({url:cotefe.apiurl+"me"+"?access_token="+cotefe.token});						//user
	ProjectList=ResourceList.extend({url:cotefe.apiurl+"projects/?access_token="+cotefe.token});		//projects list
	ExperimentList=ResourceList.extend({url:cotefe.apiurl+"experiments/?access_token="+cotefe.token});	//experiment list
	JobList=ResourceList.extend({url:cotefe.apiurl+"jobs/?access_token="+cotefe.token});				//jobs list
	ImageList=ResourceList.extend({url:cotefe.apiurl+"images/?access_token="+cotefe.token});				//jobs list
	
	
	
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
			case "image":url=cotefe.apiurl+"images/?access_token="+cotefe.token; break;
		}
		
		//resource=new Resource({name:name,description:description,project_id:8});
		//resource=new Resource({name:name,description:description,experiment_id:9,testbed_id:"twist",datetime_from:"2012-05-15T13:00:00+0000",datetime_to:"2012-05-15T15:00:00+0000"});
		resource=new Resource({name:name,description:description});
		resource.url=url;
		resource.save({success:function(){alert("Successfully saved");}});
		
		
	}
	
	
	/*
	 * put model
	 */
	
	putModel=function(type,text)
	{	
		tem={};
		obj= JSON.parse(text);
		var count = 0;
		for (var attr in obj) {
		    if (obj.hasOwnProperty(attr)) {
		    	tem[attr]=obj[attr];
		    }
		}
		res=new Resource(tem);
		res.url=tem.uri+"?access_token="+cotefe.token;
		res.save({success:function(){alert("Successfully updated");}});
		
	}
	
	
	resourcetype = function(type)
	{
		
		resourceList=null;
		dom_id="";
		switch(type)
		{
			case "project": resourceList=new ProjectList();dom_id="#projects";break;
			case "experiment":resourceList=new ExperimentList();dom_id="#experiments";break;
			case "job":resourceList=new JobList();dom_id="#jobs";break;		
			case "image":resourceList=new ImageList();dom_id="#images";break;		
		}
		resourceList.display(dom_id);		
		
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
			case "job":			single_job=new Resource();
								single_job.url=cotefe.apiurl+"jobs/"+id+"?access_token="+cotefe.token;
								single_job.display("#jobs");
								break;
			case "image":		single_job=new Resource();
								single_job.url=cotefe.apiurl+"images/"+id+"?access_token="+cotefe.token;
								single_job.display("#images");
								break;
		
		}
		
	}
	
	removeResource = function (id,type)
	{
		id=id.trim();
		resource=new Resource();;
		switch(type)
		{
			case "project": 	resource.url=cotefe.apiurl+"projects/"+id+"?access_token="+cotefe.token;
	        					break;
			case "experiment":	resource.url=cotefe.apiurl+"experiments/"+id+"?access_token="+cotefe.token;
								break;
			case "job":			resource.url=cotefe.apiurl+"jobs/"+id+"?access_token="+cotefe.token;
								break;
			case "image":		resource.url=cotefe.apiurl+"images/"+id+"?access_token="+cotefe.token;
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
	
	token=function()
	{
		return cotefe.token;
	}
	c_url=function()
	{
		return cotefe.requesturl;
	}

})(jQuery)



$(document).ready(function(){
   
	
	$("input[name=token]").val(token());
	$("input[name=url]").val(c_url());
	
   usera= new User();   
   usera.display("#userContent");

   $('input[type=button]').click(function(){
   				element=$(this).parents('form');
   				type=(element.attr("class"));
   				method=$(this).attr('name');
   				
   				switch(method)
   				{
   					case 'GET':		checkInput(this)!=false?resourceSingleItem(checkInput(this),type):resourcetype(type);break;
   					case 'POST': 	postModel(type);break;
   					case 'PUT':		putModel(type,$(("#"+type+"s")).val());break;
   					case 'DELETE':	checkInput(this)!=false?removeResource(checkInput(this),type):alert("NO ID provided");break;
   				
   				}
   				
   				
   				
   			});
   
   
	
	/*
	 * slide form DIV
	 */
	$("h3").on("click",function(){$(this).next("form").slideToggle("fast");});

   
 });



