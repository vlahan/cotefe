//jQuery.noConflict();

/*
 * dom events 
 * start events for page
 * 
 */

jQuery(document).ready(function(){  
	init();
});


function init()
{
	/*
	 * set current user name
	 */
	//if(currentUser()!=null)
		//$("#currentUser").html(currentUser());
	
	/*
	 * left menu events
	 */
	leftMenu();
	
	/*
	 * init dashboard content
	 */
	initDashBoard();
	
	
}

function printValue(source,destination)
{
	this.document.getElementById(destination).innerHTML=(this.document.getElementById(source).value);
}

/*
 * left menu event add and handler
 */
function leftMenu()
{
	$("#nav a").click(function(event) {
		  event.preventDefault();
		  var ids=($(this).attr('id'));
		  leftMenuActionHandler(ids);
	});
	$('#nav a').on("click",function(event) {$(this).next().toggle('fast');}).next().hide();
	
	
	
}
function tabsEvent()
{
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
}
function imageButtonEvent()
{
	$("#pic-button a").click(
		function(event){
		   event.preventDefault();
		   event.stopPropagation();
		   var cl=($(this).attr("class"));
		   var par=cl.split(" ");
		   var selector=(par[0]);
		   switch(selector)
		   {
		   	case "project"		:addProject();break;
		   	case "experiment"	:break;
		   	case "jobs"			:break;
		   	case "images"		:break;
		   }
		});
}
function editDeleteEvent()
{
	$(".edit,.delete,.newIm").bind('click', function(event) {
		   event.preventDefault();
		   event.stopPropagation();  
		   var classname=$(this).attr("class");
		   if(classname=="newIm")
		   {
		   		var itemtype=$(this).attr("title");
		   		switch(itemtype)
		   		{
		   			case "project":addProject();break;
		   		}
		   }
		   else if(classname=="edit")
		   {
		   		var itemuri=$(this).attr("href");
		   		updateProject(itemuri);
		   }
	});
	
}


function leftMenuActionHandler(selector)
{
	switch(selector)
	{
		case "dashboard"	:break;
		case "homescreen"	:initDashBoard();break;
		case "myaccount"	:break;
		case "settings"		:break;
		case "signout"		:signOut();break;
		case "projects"		:break;
		case "addP"			:addProject(null);break;
		case "listP"		:listProject();break;
		case "experiments"	:break;
		case "addE"			:break;
		case "listeE"		:break;
		case "jobs"			:break;
		case "addJ"			:break;
		case "listJ"		:break;		
		case "images"		:break;
		case "uploadIm"		:break;
		case "listIm"		:break;
	}
}




function addEvent()
{
	tabsEvent();
	editDeleteEvent();
	imageButtonEvent();
}

function updateProject(val)
{
	var obj=getItemFromLocal("cotefeProjects",val);
	ajaxFunction("GET","../htmls/projectsNew_tpl.html",null,null,
	function(uri,data){
		$("#content").empty().append(data);addEvent();
		$('input[name=uri]').val(obj.uri);
		$('input[name=name]').val(obj.name);
		$('textarea[name=description]').val(obj.description);
		//submitEventonLoad();
	}); 
}

function submitEventonLoad()
{
	$("form").submit(function(event) {
		event.preventDefault();event.stopPropagation();
     	var uri=$("input[name=uri]").val();
     	if(uri=="" || uri == undefined || uri== null)
     	{
     		//new resource
     		var link="";
     		var saveData = {};
     		$(":input").each(
     			function(){
     				if($(this).attr("name")=="uri" ||
     				 $(this).attr("name")=="submit" ||
     				 $(this).attr("name")=="type")
     				{

     				}
     				else
     				{     				
						saveData[$(this).attr("name")] = $(this).val();
					}
     			});
     			
     			alert(JSON.stringify(saveData)+"   "+makeLink($("input[name=type]").val()));
     			//send data
     			url=makeLink($("input[name=type]").val())+"?access_token="+getToken();
     			$.ajax({
				  type: 'POST',
				  url: url,
				  data: JSON.stringify(saveData),
				  success: function(data){alert("posted");},
				});
     			//ajaxFunction("post",makeLink($("input[name=type]").val()),getToken(),JSON.stringify(saveData),null);
     			//set local
     	}
     	else
     	{
     		//update resource
     		
     	}
    });
}


function NotifyResultOfPost()
{
	
}
