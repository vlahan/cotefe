/**
 * after token saved and dashboard loaded
 */

function getToken()
{
	return sessionStorage.getItem('access_token');
}

$(document).ready(function(){
	
	/*
	 * user info of dashboard
	 */
	res=new  cotefe.Resource({model:cotefe.Resource});
	res.url=cotefe.apiUri+cotefe.user.uri+"?access_token="+getToken();
	res.display("",DashBoardView);

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
events.disableAnchor		=function(params){
	$("#sidebar, #content").on("click",function(event){event.preventDefault();event.stopPropagation();});
};
/*
 * views
 */
var DashBoardView =Backbone.View.extend({
	
	el:'#userWelcomeText',
	content:'#content',
	initialize:function(){_.bindAll(this,"render");this.render();},
	render:function()
	{		
		var data={
				first		: this.model.attributes.first,
				last		: this.model.attributes.last,				
			};		
		menu = new EJS({url: '../templates/greetTemplate.ejs'}).render(data);
		$(this.el).html(menu);
		//console.log(this.model);
		projects=this.model.attributes.projects;
		experiments=this.model.attributes.experiments;
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
				imagedata			: new EJS({url: '../templates/imageMenu.ejs'}).render(),
				projecttable		: new EJS({url: '../templates/tableModel.ejs'}).render(datap),	
				exptable			: new EJS({url: '../templates/tableModel.ejs'}).render(datae),
			};
		
		menu = new EJS({url: '../templates/dashboard.ejs'}).render(data);
		$(this.content).html(menu);
		events.leftMenu();
		events.initSignOut();
		events.tabs();
		events.disableAnchor();
	}
	
});