/**
 * after token saved and dashboard loaded
 */

function getToken()
{
	if(sessionStorage.getItem('access_token'))
		return sessionStorage.getItem('access_token');
	else
		{
			cotefe.signOut();
		}
}

$(document).ready(function(){
	
	/*
	 * user info of dashboard
	 */
	res=new  cotefe.Resource({model:cotefe.Resource});
	res.url=cotefe.apiUri+cotefe.user.uri+"?access_token="+getToken();
	res.display("",DashBoardGreetView);
	
	/*
	 * content for dashboard
	 */
	res=new  cotefe.Resource({model:cotefe.Resource});
	res.url=cotefe.apiUri+cotefe.user.uri+"?access_token="+getToken();
	res.display("",DashBoardContentView);
	/*
	 * content event for left Menu
	 */
	new LeftMenuView();
	
});

/*
 * events
 */

events					={};
events.leftMenu			=function(){
	$("#nav a").click(function(event) {
         event.preventDefault();
         var ids=($(this).attr('id'));
         //handler.leftMenu(ids);
   });
   $('#nav a').on("click",function(event) {$(this).next().toggle('fast');}).next().hide();   
};
events.initSignOut				=function(){
	$("#signout").bind("click",function(event){event.preventDefault();cotefe.signOut();});
};
events.tabs				=function(){
	$(".tab_content").hide(); 
    $("ul.tabs li:first").addClass("active").show(); 
    $(".tab_content:first").show(); 

    //On Click Event
    $("ul.tabs li").on("click",function(event) {
        
        $("ul.tabs li").removeClass("active"); 
        $(this).addClass("active"); 
        $(".tab_content").hide(); 

        var activeTab = $(this).find("a").attr("href");
        $(activeTab).fadeIn(); 
        return false;
    });
};



/*
 * dashboard views
 */
var DashBoardGreetView=Backbone.View.extend({
	
	el:'#userWelcomeText',
	
	
	initialize:function(){_.bindAll(this,"render");this.render();},
	
	render:function()
	{		
		var data={
				first		: this.model.attributes.first,
				last		: this.model.attributes.last,				
			};		
		menu = new EJS({url: '../templates/greetTemplate.ejs'}).render(data);
		$(this.el).html(menu);
	}
	
});
var DashBoardContentView =Backbone.View.extend({
	
	el:'#content',
	
	initialize:function(){_.bindAll(this,"render");
			$(this.el).undelegate('#content .edit', 'click');
			$(this.el).undelegate('#content .delete', 'click');
			this.render();
	},
	events:{
		"click #content #projects .edit":'editp',
		"click #content #projects .delete":'deletep',
		"click #content #experiments .edit":'edite',
		"click #content #experiments .delete":'deletee',
		"click #content #jobs .edit":'editj',
		"click #content #jobs .delete":'deletej',
	},
	editp:function(event) { 
		event.preventDefault();
		
		res=new  cotefe.Resource();
		res.url=event.target+"?access_token="+getToken();
		res.display("",ProjectEdit);
		
	},
	deletep:function(event)
	{
		event.preventDefault();
		var delres=new  cotefe.Resource();
		var path=(event.target.attributes[0].nodeValue);
		delres.id=2000002;
		delres.url=path+"?access_token="+getToken();
		console.log(delres);
		delres.destroy({
				success : _.bind(function(model, response) {
					console.log("Success");
	                console.log(model);
	            }, this),
	            error : _.bind(function(model, response) {
	            	console.log("Error");
				  	console.log(model);
			    }, this)
		});
	},
	edite:function(event) { 
		event.preventDefault();
		res=new  cotefe.Resource();
		res.url=event.target+"?access_token="+getToken();
		res.display("",ExperimentEdit);
		
	},
	deletee:function(event)
	{
		event.preventDefault();
		res=new  cotefe.Resource();
		res.url=event.target+"?access_token="+getToken();
		res.destroy();
	},
	editj:function(event) { 
		event.preventDefault();
		res=new  cotefe.Resource();
		res.url=event.target+"?access_token="+getToken();
		res.display("",ExperimentEdit);
		
	},
	deletej:function(event)
	{
		event.preventDefault();
		res=new  cotefe.Resource();
		res.url=event.target+"?access_token="+getToken();
		res.destroy();
	},
		

	render:function()
	{	
		datai={
				projects:"projects",
				experiments:"experiments",
				jobs:"jobs",
				images:"images"
		}
		
		projects=this.model.attributes.projects;
		experiments=this.model.attributes.experiments;
		sessionStorage.setItem("user",JSON.stringify(this.model));
		row=5;//minimum line to display
		datap={
				type:"projects",
				headings:['Project Name','Edit','Delete'],
				objects:projects,				
		}
		datae={
				type:"experiments",
				headings:['Experiment Name','Edit','Delete'],
				objects:experiments,				
		}
		
		
		var data={
				imagedata			: new EJS({url: '../templates/imageMenu.ejs'}).render(datai),
				projecttable		: new EJS({url: '../templates/tableModel.ejs'}).render(datap),	
				exptable			: new EJS({url: '../templates/tableModel.ejs'}).render(datae),
			};
		
		menu = new EJS({url: '../templates/dashboard.ejs'}).render(data);
		$(this.el).html(menu);
		//events.leftMenu();
		events.initSignOut();
		events.tabs();
		
	}
	
});
var LeftMenuView=Backbone.View.extend({
	el:'#sidebar',
	
	initialize:function(){_.bindAll(this,"render");this.render();},
	events:{
		"click #signout":'signout',
		"click #homescreen":function(){res=new  cotefe.Resource({model:cotefe.Resource});
							res.url=cotefe.apiUri+cotefe.user.uri+"?access_token="+getToken();
							res.display("",DashBoardContentView);},
		"click #addP":function(){res=new  ProjectEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/projects/",type:"projects",description:"",name:""})});},
		"click #addE":function(){res=new  ExperimentEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/experiments/",type:"experiments",description:"",name:"",selected:"",projects:""})});},		
	},
	signout:function(event) { event.preventDefault();cotefe.signOut();},
	render:function()
	{		
		var data={};		
		menu = new EJS({url: '../templates/leftmenu.ejs'}).render(data);
		$(this.el).html(menu);
		$("#nav a").click(function(event) {
	         event.preventDefault();
	         var ids=($(this).attr('id'));
	   });
	   $('#nav a').on("click",function(event) {$(this).next().toggle('fast');}).next().hide();   
	}
	
});
var ProjectEdit=Backbone.View.extend({
	el:"#content",
	initialize:function(){_.bindAll(this,"render");this.render();$(this.el).undelegate('input[name=submit]', 'click');
},
	events:
		{
			"click input[name=submit]":'submit',		
		},
		
	submit:function(event){
		event.preventDefault();	
		console.log(event.target);
		url="";
		temprory=($("#projectform").serializeArray());
		for(i =0;i<temprory.length;i++)
			{
				if(temprory[i].name=="uri")
					{
						url=temprory[i].value;
						
					}
				else if(temprory[i].name=="type")
					{
						continue;
					}
				this.model.attributes[temprory[i].name]=temprory[i].value;
				
			}
		
		res=this.model;	
		
		res.url=url+"?access_token="+getToken();
		res.save({success:function(){alert("Successfully updated");}});
		
	},	
	render:function()
	{	
		data={
				uri			:this.model.attributes.uri,
				type		:"projects",
				name		:this.model.attributes.name,
				description	:this.model.attributes.description,
		},
		
		menu = new EJS({url: '../templates/projectNew.ejs'}).render(data);
		$(this.el).html(menu);
	}
	
});
var ExperimentEdit=Backbone.View.extend({
	el:"#content",
	initialize:function(){_.bindAll(this,"render");this.render();$(this.el).undelegate('input[name=submit]', 'click');
},
	events:
		{
			"click input[name=submit]":'submit',		
		},
		
	submit:function(event){
		event.preventDefault();	
		url="";
		temprory=($("#experimentform").serializeArray());
		for(i =0;i<temprory.length;i++)
			{
				if(temprory[i].name=="uri")
					{
						url=temprory[i].value;
						
					}
				else if(temprory[i].name=="type")
					{
						continue;
					}
				this.model.attributes[temprory[i].name]=temprory[i].value;
				
			}
		
		res=this.model;	
		
		res.url=url+"?access_token="+getToken();
		res.save({success:function(){alert("Successfully updated");}});
		
	},	
	render:function()
	{	
		
		data={
				uri			:this.model.attributes.uri,
				type		:"experiments",
				name		:this.model.attributes.name,
				selected	:this.model.attributes.project,
				description	:this.model.attributes.description,
		},
		
		menu = new EJS({url: '../templates/experimentNew.ejs'}).render(data);
		$(this.el).html(menu);
	}
	
});
