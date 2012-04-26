(function($){
	
	var cotefe = {
			baseurl:"http://localhost:8080",
			apiurl: "https://api.cotefe.net/",
			token : "1908700504b2474e9e9d6cc6225d3ece",
			
		};
	
	/*
	 * models
	 */
	userInfo = Backbone.Model.extend({
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
	
	project  = Backbone.Model.extend({
				url:cotefe.apiurl+"projects/?access_token="+cotefe.token,
				uri: "https://api.cotefe.net/projects/47001",
				media_type: "application/json",
				name: "blabla",
				id: 47001,
				description: "hey there fdagra",
				owner: {},
				experiments:[],
				experiment_count: 1,
				datetime_created: "2012-04-18T09:47:14+0000",
				datetime_modified: "2012-04-18T09:47:24+0000",
				display: function() {
				    this.fetch({
				      	success: function(model, response) {
				      		new ProjectView({model:model});
				      			//console.log(model);
				        		return (model);
				      		}
			    		});
			  		}
		  });
	
	experiemnt=Backbone.Model.extend({
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
	
	
	
	
	/*
	 *
	 */
	
	/*
	 * template
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
	 

})(jQuery)
$(document).ready(function(){
   
   user= new userInfo();
   
   user.display();
   //proj= new project();
   //proj.display();
   //exp= new experiemnt();
   //exp.display();
   
   $('input[type=button]').click(function(){
   				element=$(this).parents('form');
   				type=(element.attr("class"));
   				method=$(this).attr('name');
   				if(method=="GET")
   				{
   					//check next box
   					text=$(this).next('input[type=text]').val();
   					if(text!="")
   					{
   						projects=new project();
   						projects.url="https://api.cotefe.net/projects/"+text+"?access_token=1908700504b2474e9e9d6cc6225d3ece";
   						projects.display();
   						//console.log(projects.get('url'));
   					}
   					else
   					{
   						projects=new project({'url':"https://api.cotefe.net/projects/?access_token=1908700504b2474e9e9d6cc6225d3ece"});
   						projects.display();
   					}
   				}   			
   			});
   
   
   
   
  
   
	
	
	/*
	 * slide form DIV
	 */
	$("h3").on("click",function(){$(this).next("form").slideToggle("slow");});

   
 });
