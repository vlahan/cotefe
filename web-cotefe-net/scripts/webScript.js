/*
 * web scripts for events uses jquery engine
 */
jQuery(document).ready(function(){  
    init();
});

function init(){
        initSignOut();//add sign off event
        leftMenu();//initialize left-menu
        tabsEvent();//initialize tabs
        disableanchors();//disable all anchors to follow
        greetUser();//user info
        initDashboard();//create dash-board
    };

/*
 * sign off event
 */
function initSignOut()
{
    $("#signout").bind("click",function(event){event.preventDefault();cotefe.signOut();});
};

/*
 * disable all anchors in left menu and content
 */

function disableanchors()
{
    $("#sidebar, #content").on("click",function(event){event.preventDefault();event.stopPropagation();});
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

function leftMenuActionHandler(selector)
{
    switch(selector)
    {
        case "dashboard"    :break;
        case "homescreen"   :initDashboard();break;
        case "myaccount"    :break;
        case "settings"     :break;
        case "signout"      :signOut();break;
        case "projects"     :break;
        case "addP"         :addProject(null);break;
        case "listP"        :displayProjectList();break;
        case "experiments"  :break;
        case "addE"         :break;
        case "listeE"       :break;
        case "jobs"         :break;
        case "addJ"         :break;
        case "listJ"        :break;     
        case "images"       :break;
        case "uploadIm"     :break;
        case "listIm"       :break;
    }
}

/*
 * tabs event
 */
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

/*
 * user info
 */
function greetUser()
{
    var data=cotefe.application.user;
    
            menu = new EJS({url: '../templates/greetTemplate.ejs'}).render(data);
            var navi=document.getElementById("userWelcomeText");
            navi.innerHTML=menu;
}
function capitalize (text) {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

function initDashboard()
{
            rows=5
            /*
             * image menu
             */
            var data={projects:"projects",experiments:"experiments",jobs:"jobs",images:"images"};    
            menu = new EJS({url: '../templates/imageMenu.ejs'}).render(data);
            
            /*
             * render project
             */
            cotefe.application.dumbObj=[];
            var arr=JSON.parse(sessionStorage.getItem(cotefe.localUserProject));
            for(i=0;i<arr.length;i++)
            {
                obj=JSON.parse(arr[i]);
                cotefe.application.dumbObj.push(obj)
            };
            data={
                    headings:['Project Name','Date','Edit','Delete'],
                    objects :cotefe.application.dumbObj,
                    type:cotefe.localUserProject,
                    row:rows
                 };
            table= new EJS({url: '../templates/tableModel.ejs'}).render(data);
            
            data={ imagedata:menu,projecttable:table};
            
            completepage = new EJS({url: '../templates/dashboard.ejs'}).render(data);
            var navi=document.getElementById("content");
            navi.innerHTML=completepage;            
            /*
             * render experiments
             */
            /*
             * render jobs
             */
            /*
             * render images
             */
            $(document).bind("load",dashboardEvents());
                 
};
function dashboardEvents()
{
    tabsEvent();
    editDelEvent();
    picEvent();
    addNewItemImgEvent();
}
function addNewItemImgEvent()
{
	$(".newIm").bind("click",function(event){var element=$(this).attr("href");
			switch(element)
			{
			 case "projects"     : addProject(null); break;
		     case "experiments"  : break;
		     case "jobs"         : break;
		     case "images"       : break;
			}
	});
}
function picEvent()
{
    $("#pic-button a").bind("click",function(event){
        var typ=$(this).attr("href");
        switch(typ)
        {
            case "projects"     : addProject(null); break;
            case "experiments"  : break;
            case "jobs"         : break;
            case "images"       : break;
        }
        
    });
}
function editDelEvent()
{
    $(".edit,.delete").bind("click",function(event)
                                        {
                                            var href=$(this).attr("href");
                                            var classr=$(this).attr("class");
                                            var type=$(this).attr("title");
                                            switch(classr)
                                            {
                                                case "edit"     : addProject(getItemFromStore(type,href));break;
                                                case "delete"   : break;
                                            }
                                        });
}
function addProject(val)
{
    if(val!=null)
    {
        data={uri:val.uri,type:"PUT",sessionvar:cotefe.localUserProject,name:val.name,description:val.description};
    }
    else
    {data={ uri:cotefe.projects,type:"POST",sessionvar:cotefe.localUserProject,name:"",description:""}; }
    
    completepage = new EJS({url: '../templates/projectNew.ejs'}).render(data);
    var navi=document.getElementById("content");
    navi.innerHTML=completepage;
    submitEventHandler();
    
}
function getItemFromStore(type,uri){
        switch(type)
        {
            case cotefe.localUserProject:return cotefe.session.FindItemByUri(type,uri);break;
        }
};
function displayProjectList()
         {
            cotefe.application.dumbObj=[];
            var arr=JSON.parse(sessionStorage.getItem(cotefe.localUserProject));
           
            for(i=0;i<arr.length;i++)
            {
                obj=JSON.parse(arr[i]);
                cotefe.application.dumbObj.push(obj)
            };
            row=arr.length;
            data={
                    headings:['Project Name','Date','Edit','Delete'],
                    objects :cotefe.application.dumbObj,
                    type:cotefe.localUserProject,
                    row:row
                 };
            table= new EJS({url: '../templates/tableModel.ejs'}).render(data);
            
            data={tablecontent:table};
            projlist= new EJS({url: '../templates/projectList.ejs'}).render(data);
            var navi=document.getElementById("content");
            navi.innerHTML=projlist;
            $(document).bind("load",dashboardEvents());      
         }

function submitEventHandler(form)
{
	$("input[type=submit]").bind("click",function()
			{	
				var link="";
				cotefe.application.dumbObj=[];
				
		 		$(":input").each(
		 			function(){
		 				if($(this).attr("name")=="uri" 	||
		 				 $(this).attr("name")=="submit" ||
		 				 $(this).attr("name")=="type"	||
		 				 $(this).attr("name")=="session")
		 				{
		
		 				}
		 				else
		 				{     				
		 					var key=$(this).attr("name");var value=$(this).val();
		 					
		 					cotefe.application.dumbObj.push(('"'+key+'":"'+value+'"'));
						}
		 			});
		 			payload=("{"+cotefe.application.dumbObj.join(",")+"}");
		 			
		 			sendForResourceModify($("input[name=uri]").val(),$("input[name=type]").val(),$("input[name=session]").val(),payload);	
		 		
			});
}

/*
 * sends to update localData and server
 */
function sendForResourceModify(url,type,session,json)
{
	obj=JSON.stringify(JSON.parse(json));
	bundle={url:url,method:type,session:session,payload:obj};
	cotefe.application.update(bundle);
}