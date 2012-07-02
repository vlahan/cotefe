/**
 * after token saved and dash-board loaded
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
	 * user info of dash-board
	 */
	res=new  cotefe.Resource({model:cotefe.Resource});
	res.url=cotefe.apiUri+cotefe.user.uri+"?access_token="+getToken();
	res.display("",DashBoardGreetView);
	
	/*
	 * content for dash-board
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
 * dash-board views
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
		$(this.el).html(menu).fadeIn();
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
		"click #content #experiments .edit":'edite',		
		"click #content #jobs .edit":'editj',
		"click #content .delete":'deleteResource',
		
	},
	editp:function(event) { 
		event.preventDefault();
		$(this.el).html("");
		res=new  cotefe.Resource();
		res.url=event.target+"?access_token="+getToken();
		res.display("",ProjectEdit);
		
	},
	deleteResource:function(event)
	{
		event.preventDefault();
		var delres=new  cotefe.Resource();
		var path=(event.target);
		delres.id=2000002;
		delres.url=path+"?access_token="+getToken();
		delres.destroy({
				success :function(model, response) {
					var al=new Alert({});
					al.render("alertSuccess","Resource Deletion Successfull !");
					 $('a[href="'+event.target+'"]').parent().parent().remove();
	            },
	            error :function(model, response) {
	            	var al=new Alert({});
	            	al.render("alertFail","Resource Deletion failed !");
			    },
			    
		});
		
	},
	edite:function(event) { 
		event.preventDefault();
		$(this.el).html("");
		res=new  cotefe.Resource();
		res.url=event.target+"?access_token="+getToken();
		res.display("",ExperimentEdit);
		
	},
	
	editj:function(event) { 
		event.preventDefault();
		$(this.el).html("");
		res=new  cotefe.Resource();
		res.url=event.target+"?access_token="+getToken();
		res.display("",ExperimentEdit);
		
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
		$(this.el).html(menu).fadeIn();
				
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
		res.save({ id: this.model.get('id') },{
			
			success : function(model, response) {
                var al=new Alert({});
				
                if(model.id==undefined)
                	{
                		al.render("alertSuccess","Project created successfully!");
                	}
                else
                	{
                		al.render("alertSuccess","Project updated successfully!");
                	}
                
            },
            error :function(model, response) {
            	var al=new Alert({});
				al.render("alertFail","Project create/update Failed!");
		    },
			
			
		});
		
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
		$(this.el).html(menu).fadeIn();
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
		res.save({ id: this.model.get('id') },{
					
					success : function(model, response) {
		                var al=new Alert({});
						
		                if(model.id==undefined)
		                	{
		                		al.render("alertSuccess","Experiment created successfully!");
		                	}
		                else
		                	{
		                		al.render("alertSuccess","Experiment updated successfully!");
		                	}
		                
		            },
		            error :function(model, response) {
		            	var al=new Alert({});
						al.render("alertFail","Experiment create/update Failed!");
				    },
					
					
				});
		
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
		$(this.el).html(menu).fadeIn();
	}
	
});


var Alert=Backbone.View.extend({
	
	el:'#alert-wrapper',
	initialize:function(){$("#alert").remove();},
	
	render:function(classname,message)
	{		
		var data={
				classname	: classname,
				message		: message,				
			};		
			menu = new EJS({url: '../templates/alert.ejs'}).render(data);
			$(this.el).append(menu).fadeIn().delay(3000).fadeOut(500, function(){
			      $(this.el).html("");
			  });//queue(function() {$("#alert").fadeOut();$("#alert").remove(); });
	}
	
});

