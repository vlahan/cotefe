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

function getPlatforms()
{
	var ResTestbed= new cotefe.ResourceList({model:new cotefe.Resource()});
				ResTestbed.url=cotefe.apiUri+cotefe.platforms.uri+"?access_token="+getToken();
				ResTestbed.fetch({
					success:function(collection){
					for(var i in collection.models )
						{
							var temptestbed= new cotefe.Resource();
							temptestbed.url=collection.models[i].get("uri")+"?access_token="+getToken();
							temptestbed.fetch({
								success:function(model, response)
								{
									if(sessionStorage.getItem("platforms"))
										{
											var jsonobj=JSON.parse(sessionStorage.getItem("platforms"));
											jsonobj.push(model);
											
											var arr = {};

											for ( i=0; i < jsonobj.length; i++ )
											    arr[jsonobj[i]['id']] = jsonobj[i];
											
											jsonobj = new Array();
											for ( key in arr )
											    jsonobj.push(arr[key]);
											
											sessionStorage.setItem("platforms",JSON.stringify(jsonobj));
										}
									else
										{
											var mod=[model];											
											sessionStorage.setItem("platforms",JSON.stringify(mod));
										}
								}
								
							});
						}
					
				}});
}

function getTestBeds()
{
	var ResTestbed= new cotefe.ResourceList({model:new cotefe.Resource()});
				ResTestbed.url=cotefe.apiUri+cotefe.testbeds.uri+"?access_token="+getToken();
				ResTestbed.fetch({success:function(collection){
					for(var i in collection.models )
						{
							var temptestbed= new cotefe.Resource();
							temptestbed.url=collection.models[i].get("uri")+"?access_token="+getToken();
							temptestbed.fetch({
								success:function(model, response)
								{
									if(sessionStorage.getItem("testbeds"))
										{
											var jsonobj=JSON.parse(sessionStorage.getItem("testbeds"));
											var found=false;
											for (var i in jsonobj)
												{
													if(jsonobj[i].id==model.id)
														found = true
												
												}
											if(found==false){jsonobj.push(model);}
											
											sessionStorage.setItem("testbeds",JSON.stringify(jsonobj));
										}
									else
										{
											var mod=[model];
											sessionStorage.setItem("testbeds",JSON.stringify(mod));
										}
								}
								
							});
						}
					
				}});
}

function getAllExps(experimentList)
{
	
	for(var i in experimentList)
		{
			var res=new  cotefe.Resource();
			res.url=experimentList[i].uri+"?access_token="+getToken();
			res.fetch({
				success:function(model){
					getExperimentSets(model,false);
					
				}
			});
			
		}
}

function getExperimentSets(model,force)
{
	
			/*
			 * load all of the resources
			 * dig deep
			 */

			var experiments=new Array();
			if(sessionStorage.getItem("experiments"))
				{
					var explist=JSON.parse(sessionStorage.getItem("experiments"));
					var exists=false;
					for(var i in explist)
						{
						
							if(explist[i].id===model.get("id") && force === false)
								{
									exists=true;
								}
							if(explist[i].id===model.get("id") && force===true)
								{
								
									explist.splice(i, 0, model);
								}
						
						}
					if(exists===false)
						{
							explist.push(model);
						}
					sessionStorage.setItem("experiments",JSON.stringify(explist));
				}
			else
				{
						experiments.push(model);
						sessionStorage.setItem("experiments",JSON.stringify(experiments));
				}
					
}


$(document).ready(function(){
	
	/*
	 * user info of dash-board
	 */
	res=new  cotefe.Resource();
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
	
	/*
	 * get all platforms as first place
	 */
	getPlatforms();
	/*
	 * get all test beds right away
	 */
	getTestBeds();
	
	
});


/*
 * print value
 */
function printValue(arg0,arg1)
{
	var textbox= document.getElementById(arg1);
	textbox.value=arg0;
	
}


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

function UpdateSession(data)
{
	if( sessionStorage.getItem("user"))
		{
			sessionStorage.setItem("user",data);	
		
		}
}

/*
 * dash-board views
 */
var DashBoardGreetView		=Backbone.View.extend({
	
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

var DashBoardContentView	=Backbone.View.extend({
	
	el:'#content',
	
	initialize:function(){_.bindAll(this,"render");
			$(this.el).undelegate('#content .edit', 'click');
			$(this.el).undelegate('#content .delete', 'click');
			$(this.el).undelegate('#content #pic-button .project', 'click');
			$(this.el).undelegate('#content #pic-button .experiment', 'click');
			$(this.el).undelegate('#content #pic-button .jobs', 'click');
			$(this.el).undelegate('#content #pic-button .images', 'click');
			
			
			this.render();
	},
	events:{
		"click #content #projects .edit":'editp',		
		"click #content #experiments .edit":'edite',
		"click #content .experimentResource":'getpropertySet',			
		"click #content #jobs .edit":'editj',
		"click #content .delete":'deleteResource',
		"click #content #pic-button .project":function(){event.preventDefault();res=new  ProjectEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/projects/",type:"projects",description:"",name:""})});},
		"click #content #pic-button .experiment":function(){event.preventDefault();res=new  ExperimentEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/experiments/",type:"experiments",description:"",name:"",selected:"",projects:""})});},		
		"click #content #pic-button .jobs":function(){event.preventDefault();res=new  JobEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/jobs/",type:"jobs",description:"",name:"",experiment:"",testbed:"",datetimefrom:"",datetimeto:""})});},
		"click #content #pic-button .images":function(){event.preventDefault();res=new  ImageEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/images/",type:"images",description:"",name:""})});},		
					
		
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
		
		var expurl=$('a[href="'+event.target+'"]').parent().parent().children('td').eq(1).children('a').eq(0).attr("href");
		
		delres.destroy({
				success :function(model, response) {
					var al=new Alert({});
					al.render("alertSuccess","Resource Deletion Successfull !");
					var obj_type=$('a[href="'+event.target+'"]').parent().parent().parent().parent().attr("id");
					if(obj_type==="images")
						{
							/*
							 * update experiment in session
							 */
							var newexp= new cotefe.Resource();
							newexp.url=expurl+"?access_token="+getToken();
							
							newexp.fetch({
								success:function(model){
									
									getExperimentSets(model,true);
								}
							});
						
						}
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
	
	getpropertySet:function(event){
		event.preventDefault();
		$(this.el).html("");
		res=new  cotefe.Resource();
		res.url=event.target+"?access_token="+getToken();
		res.display("",ExperimentPropertySet);
		
		/*res.fetch({
			      	success: function(model,response) {
			      			console.log(model);
			      		}
		    		});*/
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
		
		if(!sessionStorage.getItem("experiments"))
		{
			var projectssession=JSON.parse(sessionStorage.getItem("user")).experiments;
			row=projectssession.length;			
			getAllExps(projectssession);
		}
		
		var imagesObjectList=JSON.parse(sessionStorage.getItem("experiments"));
		var imageArray= new Array();
		for(var i in imagesObjectList)
			{
				for(var j in imagesObjectList[i].images){
					imageArray.push({"experiment_uri":imagesObjectList[i].uri,"experiment_name":imagesObjectList[i].name,"images":imagesObjectList[i].images[j]});
				}
			}
		
		dataimg={
				
				type:"images",
				headings:['Image Name','Experiment','Edit','Delete'],
				objects:imageArray,				
		};
		
		
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
				exptable			: new EJS({url: '../templates/tableModelex.ejs'}).render(datae),
				imageTable			: new EJS({url: '../templates/imageList.ejs'}).render(dataimg),
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
		"click #homescreen , #dashboard":function(){res=new  cotefe.Resource();
							res.url=cotefe.apiUri+cotefe.user.uri+"?access_token="+getToken();
							res.display("",DashBoardContentView);},
		"click #addP":function(){res=new  ProjectEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/projects/",type:"projects",description:"",name:""})});},
		"click #listP":function(){res=new  cotefe.Resource();
								 res.url=cotefe.apiUri+cotefe.projects.uri+"?access_token="+getToken();
								 res.display("",ProjectList);},
		"click #addE":function(){res=new  ExperimentEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/experiments/",type:"experiments",description:"",name:"",selected:"",projects:""})});},		
		"click #listE":function(){res=new  cotefe.Resource();
		 res.url=cotefe.apiUri+cotefe.experiments.uri+"?access_token="+getToken();
		 res.display("",ExperimentList);},
		 "click #addJ":function(){res=new  JobEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/jobs/",type:"jobs",description:"",name:"",experiment:"",testbed:"",datetimefrom:"",datetimeto:""})});},		
		 "click #listJ":function(){res=new  cotefe.Resource();
		 res.url=cotefe.apiUri+cotefe.jobs.uri+"?access_token="+getToken();
		 res.display("",JobsList);},
		 "click #uploadIm":function(){res=new  ImageEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/projects/",type:"projects",description:"",name:""})});},
		 "click #listIm":function(){res=new  ImageList();},
		 "click #testbeds":function(){var testres=new TestBedList({model:new cotefe.Resource()});testres.render(); },
		 "click #platforms":function(){var testres=new PlatformsList({model:new cotefe.Resource()});testres.render(); },
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

var ProjectList=Backbone.View.extend({
	el:"#content",
	initialize:function(){_.bindAll(this,"render");this.render();
		$(this.el).undelegate('.headings a', 'click');
		},
	events:{
		"click .headings a":function(event){event.preventDefault();
			res=new  ProjectEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/projects/",type:"projects",description:"",name:""})});
		},
	},
	render:function()
	{	
		
		
		var projectssession=JSON.parse(sessionStorage.getItem("user")).projects;
		row=projectssession.length;
		
		datap={
				
				type:"projects",
				headings:['Project Name','Edit','Delete'],
				objects:projectssession,				
		};
		
		menu = new EJS({url: '../templates/tableModel.ejs'}).render(datap);	
		
		listing = new EJS({url: '../templates/projectList.ejs'}).render({tablecontent:menu,imlink:"#",tableheader:"Projects"});
		$(this.el).html(listing).fadeIn();
	}
	
});

var ExperimentList=Backbone.View.extend({
	el:"#content",
	initialize:function(){_.bindAll(this,"render");this.render();
	$(this.el).undelegate('.headings a', 'click');
	
	},
	events:{
		"click .headings a":function(event){event.preventDefault();
		res=new  ExperimentEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/experiments/",type:"experiments",description:"",name:"",selected:"",projects:""})});
		},
	},
	render:function()
	{	
		
		
		var projectssession=JSON.parse(sessionStorage.getItem("user")).experiments;
		row=projectssession.length;
		
		
		datap={
				
				type:"experiments",
				headings:['Experiment Name','Edit','Delete'],
				objects:projectssession,
		};
		
		menu = new EJS({url: '../templates/tableModelex.ejs'}).render(datap);	
		
		listing = new EJS({url: '../templates/projectList.ejs'}).render({tablecontent:menu,imlink:"#",tableheader:"Experiments"});
		$(this.el).html(listing).fadeIn();
		getAllExps(projectssession);
		
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
		
		if(sessionStorage.getItem("user"))
			projects=JSON.parse(sessionStorage.getItem("user")).projects;
		data={
				uri			:this.model.attributes.uri,
				type		:"experiments",
				name		:this.model.attributes.name,
				selected	:this.model.attributes.project,
				description	:this.model.attributes.description,
				projects	:projects
		},
		
		menu = new EJS({url: '../templates/experimentNew.ejs'}).render(data);
		$(this.el).html(menu).fadeIn();
	}
	
});




var ExperimentPropertySet=Backbone.View.extend({
	el:"#content",
	initialize:function(){_.bindAll(this,"render");this.render();$(this.el).undelegate('input[name=submit]', 'click');
						$(this.el).undelegate('.headings a', 'click');
						$(this.el).undelegate('#content .edit', 'click');
						
		},
	events:
		{
			"click input[name=submit]":'submit',
			"click .headings a":function(event){event.preventDefault();
						res=new  ExperimentEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/experiments/",type:"experiments",description:"",name:"",selected:"",projects:""})});
					},
			//s"click .edit":"",				
		},
		
	submit:function(event){
		event.preventDefault();	
		alert("Sensor not yet defined");		
	},
	loadPropertySets:function(model)
	{
		var psets=model.property_sets;
		
		
	},	
	render:function()
	{		
		//console.log(this.model);
		getExperimentSets(this.model,false);
		var e_experiments=null;
		var e_propertySets=null;
		if(sessionStorage.getItem("user"))
		{
			e_experiments=JSON.parse(sessionStorage.getItem("user")).experiments;
			platforms=JSON.parse(sessionStorage.getItem("platforms"));
		}
		
		data={
				exps:e_experiments,
				model:JSON.stringify(this.model),
				platforms:platforms,
				propertySets:"",
				virtualNodeGroups:"",
				images:"",
				virtualTasks:""
				
		},
		
		menu = new EJS({url: '../templates/experimentres.ejs'}).render(data);
		$(this.el).html(menu).fadeIn();
		events.tabs();
		
	}
	
});


/**jobs*/
var JobEdit=Backbone.View.extend({
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
		temprory=($("#jobform").serializeArray());
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
		
		if(sessionStorage.getItem("user"))
		{
			experiment=JSON.parse(sessionStorage.getItem("user")).experiments;
			getTestBeds();
			testbeds=JSON.parse(sessionStorage.getItem("testbeds"));
		}
		data={
				uri			:this.model.attributes.uri,
				type		:"jobs",
				name		:this.model.attributes.name,
				selected	:this.model.attributes.experiments,
				selectedbed	:this.model.attributes.testbeds,
				description	:this.model.attributes.description,
				experiments	:experiments,
				testbeds	:testbeds,
				datetime_from:"",
				datetime_to:""
				
		},
		
		menu = new EJS({url: '../templates/jobNew.ejs'}).render(data);
		$(this.el).html(menu).fadeIn();
	}
	
});

var JobsList=Backbone.View.extend({
	el:"#content",
	initialize:function(){_.bindAll(this,"render");this.render();
	$(this.el).undelegate('.headings a', 'click');
	
	},
	events:{
		"click .headings a":function(event){event.preventDefault();
		res=new  ExperimentEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/experiments/",type:"experiments",description:"",name:"",selected:"",projects:""})});
		},
	},
	render:function()
	{	
		
		
		var projectssession=JSON.parse(sessionStorage.getItem("user")).experiments;
		row=projectssession.length;
		
		
		datap={
				
				type:"jobs",
				headings:['Job Name','Edit','Delete'],
				objects:projectssession,
		};
		
		menu = new EJS({url: '../templates/tableModelex.ejs'}).render(datap);	
		
		listing = new EJS({url: '../templates/projectList.ejs'}).render({tablecontent:menu,imlink:"#",tableheader:"Jobs"});
		$(this.el).html(listing).fadeIn();
	}
	
});


/*
 * images upload/edit and list
 */


var ImageEdit=Backbone.View.extend({
	el:"#content",
	initialize:function(){_.bindAll(this,"render");this.render();$(this.el).undelegate('input[name=submit]', 'click');
	$(this.el).undelegate('input[name=generateLink]', 'click');
		},
	events:
		{
			"click input[name=generateLink]":'generateLink',	
			"click input[name=submit]":'submit',
		},
	
	generateLink:function(){
		event.preventDefault();	
		url="";
		temprory=($("#imageform").serializeArray());
		url=cotefe.apiUri+cotefe.experiments.uri+$.trim(temprory[3].value)+cotefe.images.uri;
		
		
		res=this.model;	
		this.model.set("type","image");
		this.model.set("uri",url);
		this.model.set("name",$.trim(temprory[2].value));
		this.model.set("description",$.trim(temprory[4].value));
		res.url=url+"?access_token="+getToken();
		//console.log(res);
		
		res.save({ id: this.model.get('cid') },{
					
					success : function(model, text, XHR) {
						
		                var al=new Alert({});
						
						al.render("alertSuccess","Please Upload your file now");
						$('<iframe id="resultFrame"/>').appendTo('#uploadLink')
                        .contents().find('body').append('<form enctype="multipart/form-data" method="post" action="'+model.get("uploadLink")+"/upload?access_token="+getToken()+'" ><input type="file" name="imagefile" /><input type="submit" value="Upload" /></form>');
						var newexp= new cotefe.Resource();
						newexp.url=cotefe.apiUri+cotefe.experiments.uri+$.trim(temprory[3].value)+"?access_token="+getToken();
						//console.log(newexp.url);
						newexp.fetch({
							success:function(model1){
							
								getExperimentSets(model1,true);
							}
						});
						
		            },
		            error :function(model1, response) {
		            	var al=new Alert({});
						al.render("alertFail","Image create/update Failed!");
				    },
					
					
				});
		
	},	
	submit:function(event){
		event.preventDefault();	/*
		url="";
		temprory=($("#imageform").serializeArray());
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
                		
                		
                		al.render("alertSuccess","Image source created successfully!");
                	}
                else
                	{
                		al.render("alertSuccess","Image spurce updated successfully!");
                	}
                
            },
            error :function(model, response) {
            	var al=new Alert({});
				al.render("alertFail","Image create/update Failed!");
		    },
			
			
		});*/
		
	},	
	render:function()
	{	
		data={
				uri			:this.model.attributes.uri,
				type		:"images",
				name		:this.model.attributes.name,
				description	:this.model.attributes.description,
		},
		
		menu = new EJS({url: '../templates/imageUpload.ejs'}).render(data);
		$(this.el).html(menu).fadeIn();
	}
	
});

var ImageList=Backbone.View.extend({
	el:"#content",
	initialize:function(){_.bindAll(this,"render");this.render();
		$(this.el).undelegate('.headings a', 'click');
		
		},
	events:{
		"click .headings a":function(event){event.preventDefault();
		res=new  ImageEdit({model:new cotefe.Resource({uri:cotefe.apiUri+"/images/",type:"images",description:"",name:""})});
		},
	},
	render:function()
	{	
		
		if(!sessionStorage.getItem("experiments"))
		{
			var projectssession=JSON.parse(sessionStorage.getItem("user")).experiments;
			getAllExps(projectssession);
		}
		
		
		
		var imagesObjectList=JSON.parse(sessionStorage.getItem("experiments"));
		
		var imageArray= new Array();
		for(var i in imagesObjectList)
			{
				for(var j in imagesObjectList[i].images){
					imageArray.push({"experiment_uri":imagesObjectList[i].uri,"experiment_name":imagesObjectList[i].name,"images":imagesObjectList[i].images[j]});
				}
			}
		row=imageArray.length;
		
		datap={
				
				type:"images",
				headings:['Image Name','Experiment','Edit','Delete'],
				objects:imageArray,				
		};
		
		menu = new EJS({url: '../templates/imageList.ejs'}).render(datap);	
		
		listing = new EJS({url: '../templates/projectList.ejs'}).render({tablecontent:menu,imlink:"#",tableheader:"Images"});
		$(this.el).html(listing).fadeIn();
	}
	
});

/*
 * testbed list view
 */


var TestBedList=Backbone.View.extend({
	el:"#content",
	events:	{
		"click #tablesubnav a":'displaydetail',
	},
	displaydetail:function(event)
	{
		event.preventDefault();
		
		var testBedResource=JSON.parse(sessionStorage.getItem("testbeds"));
		
		for(var i in testBedResource)
			{			
				if(event.target.innerHTML==testBedResource[i].name)
				{						
					var testbedd = new EJS({url: '../templates/testbedsdetails.ejs'}).render(testBedResource[i]);			
					$("#content #detail").html(testbedd).fadeIn();
				}
			}
	},
	render:function()
	{	
		var testBedResource="";
		if(sessionStorage.getItem("testbeds"))
			{
				testBedResource=sessionStorage.getItem("testbeds");
			}
		else
			{
				getTestBeds();
			}
		
		datap={
				head:"TestBeds",
				objects:JSON.parse(sessionStorage.getItem("testbeds")),				
		};
		
		menu = new EJS({url: '../templates/tableExplore.ejs'}).render(datap);			
		$(this.el).html(menu).fadeIn();
	}
	
});


/*
 * platforms list view
 */


var PlatformsList=Backbone.View.extend({
	el:"#content",
	events:	{
		//"click #tablesubnav a":'displaydetail',
	},
	displaydetail:function(event)
	{
		event.preventDefault();
		
		var testBedResource=JSON.parse(sessionStorage.getItem("platforms"));
		
		for(var i in testBedResource)
			{			
				if(event.target.innerHTML==testBedResource[i].name)
				{						
					var testbedd = new EJS({url: '../templates/testbedsdetails.ejs'}).render(testBedResource[i]);			
					$("#content #detail").html(testbedd).fadeIn();
				}
			}
	},
	render:function()
	{	
		var testBedResource="";
		if(sessionStorage.getItem("platforms"))
			{
				testBedResource=sessionStorage.getItem("platforms");
			}
		else
			{
				getPlatforms();
			}
		
		datap={
				head:"Platforms",
				objects:JSON.parse(sessionStorage.getItem("platforms")),				
		};
		
		menu = new EJS({url: '../templates/platformsdetails.ejs'}).render(datap);			
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
			res=new  cotefe.Resource();
			res.url=cotefe.apiUri+cotefe.user.uri+"?access_token="+getToken();
			res.fetch({	success: function(model, response) { UpdateSession(JSON.stringify(model));}});
		
			menu = new EJS({url: '../templates/alert.ejs'}).render(data);
			
			$(this.el).append(menu).fadeIn().delay(3000).fadeOut(500, function(){
					
					$(this.el).html("");
			  });
	}
	
});

