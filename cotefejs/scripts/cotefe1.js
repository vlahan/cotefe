(function($){
	
	var cotefe = {
			baseurl:"http://localhost:8080",
			apiurl: "https://api.cotefe.net/",
			token : "1908700504b2474e9e9d6cc6225d3ece",
			
		};
	
	/*
	 * user model
	 */
	user = Backbone.Model.extend({
					url:cotefe.apiurl+"me"+"?access_token="+cotefe.token,
					uri:"",
					media_type:"",
					username:"",
					id: 31034,
					first: "Sanjeet Raj",
					last: "Pandey",
					email: "sanjeet.raj@gmail.com",
					organization: "TKN",
					projects:[],
					experiemnts:[],
					jobs: [],
					datetime_created: "2012-02-03T17:59:46+0000",
					datetime_modified: "2012-04-18T09:37:48+0000",
				
					display: function() {
					    this.fetch({
					      	success: function(model, response) {
					      			new UserView({model:model});
					        		return (model);
					      		}
				    		});
				  	},
				
				
	      });
	
	/*
	 * a project model
	 */
	project  = Backbone.Model.extend({
				defailts:{
					url:"",
					uri: "",
					media_type: "application/json",
					name: "blabla",
					id: 47001,
					description: "hey there fdagra",
					owner: {},
					experiments:[],
					experiment_count: 1,
					datetime_created: "2012-04-18T09:47:14+0000",
					datetime_modified: "2012-04-18T09:47:24+0000"
				},
				display: function() {
				    this.fetch({
				      	success: function(model, response) {
				      		new ProjectView({model:model});
				        		return (model);
				      		}
			    		});
			  		}
		  });
	
	/*
	 * project list based on project model
	 */
	projects = Backbone.Collection.extend({				
				url:cotefe.apiurl+"projects/?access_token="+cotefe.token,				
				model:project,
		        display:function(){
		       	this.fetch({
					success: function(model,result) {	
							new ProjectListView({model:model});				      		
			      		}
		    		});
		       	
		       ;}, 
		 });
	
	/*
	 * a experiment model
	 */
	experiment = Backbone.Model.extend({
				url:cotefe.apiurl+"experiments/?access_token="+cotefe.token,
				uri: "https://api.cotefe.net/experiments/45002",
				media_type: "application/json",
				name: "Experiment1",
				id: 45002,
				description: "Experiment1",
				owner: {},
				project: {},
				images: [],
				property_sets: [],
				virtual_nodes: [],
				virtual_node_count: 0,
				virtual_node_groups: [],
				virtual_tasks: [],
				jobs: [],
				datetime_created: "2012-04-18T09:47:54+0000",
				datetime_modified: "2012-04-18T09:47:54+0000",
				display: function() {
				    this.fetch({
				      	success: function(model, response) {
				        		return (model);
				      		}
			    		});
			  		}
		 });
		
		experiments = Backbone.Collection.extend({				
				url:cotefe.apiurl+"experiments/?access_token="+cotefe.token,				
				model:experiment,
		        display:function(){
		       	this.fetch({
					success: function(model,result) {	
							new ProjectListView({el:"#experiemnts",model:model});				      		
			      		}
		    		});
		       	
		       ;}, 
		 });
	
	
	
	/*
	 *
	 */
	
	/*
	 * views 
	 */
	
	/*
	 * user view :displayed in textarea in textarea
	 */
	UserView = Backbone.View.extend({		
		el: "#userContent",		
		template:'',		
		events:{
			"click #clickme":"loaduser",
		},			
		initialize : function() {  _.bindAll(this, "render");this.render(); },
		render : function() 
		{
	    		
	    		$(this.el).append( _.template('<textarea>'+(JSON.stringify(this.model,null,'\t'))+' </textarea>',this.model.toJSON()));
	    		return this;
	    },	  	
	  	loaduser:function(){alert(JSON.stringify(this.model));}
	});
	
	
	ProjectView=Backbone.View.extend({
		el: "#projects",		
		template:'',
		initialize : function() {  _.bindAll(this, "render");this.render(); },
		render : function() 
		{
	    		
	    		$(this.el).val(JSON.stringify(this.model,null,'\t'));//_.template(JSON.stringify(this.model,null,'\t'),this.model.toJSON())
	    		return this;
	    },
	  	
	});
	
	ProjectListView=Backbone.View.extend({
		el:"#projects",
		template:'',
		initialize:function(){_.bindAll(this,"render");this.render();},
		render:function()
		{
			$(this.el).val(JSON.stringify(this.model,null,'\t'));
		}
	});

})(jQuery)
$(document).ready(function(){
   
   usera= new user();   
   usera.display();

   $('input[type=button]').click(function(){
   				element=$(this).parents('form');
   				type=(element.attr("class"));
   				method=$(this).attr('name');
   				if(method=="GET")
   				{
   					//check next box
   					text=$(this).next('input[type=text]').val();
   					if(text.trim()!="")
   					{
   						
   						single_project=new project();
   						single_project.url="https://api.cotefe.net/projects/"+text+"?access_token=1908700504b2474e9e9d6cc6225d3ece";
   						single_project.display();
   						
   					}
   					else
   					{
   						prjs=new projects();
   						prjs.display();
   						
   					}
   				}   			
   				else if(method=="POST")
   				{
   					project_new_object= new project({name:"projectnew",description:"hey new project"});
   					project_new_object.url="https://api.cotefe.net/projects/"+"?access_token=1908700504b2474e9e9d6cc6225d3ece";
   					project_new_object.save({success:function(){alert("Successfully saved");}});
   				}
   				else if(method=="PUT")
   				{
   					element=$(this).parents('form');
   					text=$(this).next('input[type=text]').val();
   					rawjson=element.next('textarea').val();
   					alert(text+"   "+rawjson);
   				}
   				else if (method=="DELETE")
   				{
   					text=$(this).next('input[type=text]').val();
   					if(text.trim()!=""){
   						single_project_delete=new project();
   						single_project_delete.url="https://api.cotefe.net/projects/"+text+"?access_token=1908700504b2474e9e9d6cc6225d3ece";
   						single_project_delete.destroy({success:function(){alert("Successfully deleted");}});
   					}
   				}
   			});
   
   
	
	/*
	 * slide form DIV
	 */
	$("h3").on("click",function(){$(this).next("form").slideToggle("slow");});

   
 });
