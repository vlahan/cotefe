/*
 * web scripts for events uses jquery engine
 */



/*******************************************/
jQuery(document).ready(function(){  
    ui.init();
});


ui							={
		projects:{id:"projects",template:"projectNew.ejs", templateVars:{uri:"",type:cotefe.projects.name,name:"",description:""}},
		experiments:{id:"experiments",template:"experimentNew.ejs", templateVars:{uri:"",type:cotefe.experiments.name,projects:cotefe.session.getValueFromKey(cotefe.projects.session),name:"",description:""}},
		
};
ui.init						=function(){
	ui.initSignOut();
	ui.events.leftMenu();
	ui.events.disableAnchor();//disable all hyperlinks in left menu and content
	ui.initUserGreet();
	ui.make.dashboard();
};
ui.initSignOut				=function(){
	$("#signout").bind("click",function(event){event.preventDefault();cotefe.signOut();});
};
ui.initUserGreet			=function(){
	var data=cotefe.session.getValueFromKey(cotefe.user.session);
	var navi=document.getElementById("userWelcomeText");
    navi.innerHTML=ui.template.render("greetTemplate.ejs",data);
};
/*
 * events
 */
ui.events					={};
ui.events.leftMenu			=function(){
	$("#nav a").click(function(event) {
         event.preventDefault();
         var ids=($(this).attr('id'));
         ui.handler.leftMenu(ids);
   });
   $('#nav a').on("click",function(event) {$(this).next().toggle('fast');}).next().hide();   
};
ui.events.tabs				=function(){
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
ui.events.disableAnchor		=function(params){
						$("#sidebar, #content").on("click",function(event){event.preventDefault();event.stopPropagation();});
					};
ui.events.pic				=function(){
	$("#pic-button a").bind("click",function(event){
        var typ=$(this).attr("href");
        switch(typ)
        {
            case "projects"     : ui.make.editNewDeleteItem(ui.projects); break;
            case "experiments"  : ui.make.editNewDeleteItem(ui.experiments); break;
            case "jobs"         : break;
            case "images"       : break;
        }
        
    });
};
ui.events.addNewItemImgEvent=function()
{
        $(".newIm").bind("click",function(event){var element=$(this).attr("href");
                        switch(element)
                        {
                         case "projects"     : ui.make.editNewDeleteItem(ui.projects); break;
	                     case "experiments"  : ui.make.editNewDeleteItem(ui.experiments); break;
	                     case "jobs"         : break;
	                     case "images"       : break;
                        }
        });
}
ui.events.addEditDelete		=function()
{
	$(".edit,.delete").bind("click",function(event)
            {
                var href=$(this).attr("href");
                var classr=$(this).attr("class");
                var elem=$(this).parent().parent().parent().parent();
                var id=$(elem).attr("id");
                
                ui.make.editNewDeleteItem({data:"filled",method:classr,id:id,uri:href});
                
            });
};
ui.events.dashboard			=function(){
	ui.events.tabs();
	ui.events.pic();
	ui.events.addNewItemImgEvent();
	ui.events.addEditDelete();
}
ui.events.submit			=function(){
	 $("input[name=submit]").bind("click",function() {
		 formobj=($('form').serializeArray());
		
		 var json = { };
		 for(index=0;index<formobj.length;index++)
			 {
			 	json[formobj[index].name] = formobj[index].value;
			 	
			 }
		
		 //pass to update and create
		 
		 ui.make.createUpdateResource(JSON.stringify(json));
	 });
};

/*
 * handlers
 */
ui.handler={};
ui.handler.leftMenu=function(selector)
{
	 switch(selector)
	    {
	        case "dashboard"    :break;
	        case "homescreen"   :ui.make.dashboard();break;
	        case "myaccount"    :break;
	        case "settings"     :break;
	        case "signout"      :cotefe.signOut();break;
	        case "projects"     :break;
	        case "addP"         :ui.make.editNewDeleteItem(ui.projects);break;
	        case "listP"        :ui.make.displayProjectList();break;
	        case "experiments"  :break;
	        case "addE"         :ui.make.editNewDeleteItem(ui.experiments);break;
	        case "listE"        :ui.make.displayExpList();break;
	        case "jobs"         :break;
	        case "addJ"         :break;
	        case "listJ"        :break;     
	        case "images"       :break;
	        case "uploadIm"     :break;
	        case "listIm"       :break;
	    }
}


/*
 * template manager
 */
ui.template			={
		dir	:	"../templates/",
};
ui.template.render	=function(filename,data)
{
	path=ui.template.dir+filename;
	return menu = new EJS({url: path}).render(data);
};



/*
 * dash-board maker
 */
ui.make					={numberOfItem:5,};
ui.make.dashboard		=function(){
	
    var data={projects:"projects",experiments:"experiments",jobs:"jobs",images:"images"};    
    menu = new EJS({url: '../templates/imageMenu.ejs'}).render(data);
    
    /*
     * render project
     */
    cotefe.application.operations.dumbList=[];
    var arr=JSON.parse(sessionStorage.getItem(cotefe.projects.session));
    for(i=0;i<arr.length;i++)
    {
        obj=JSON.parse(arr[i]);
        cotefe.application.operations.dumbList.push(obj)
    };
    data={
            headings:['Project Name','Date','Edit','Delete'],
            objects :cotefe.application.operations.dumbList,
            type:"projects",
            row:ui.make.numberOfItem
         };
    table= new EJS({url: '../templates/tableModel.ejs'}).render(data);
    
    /*
     * render experiments
     */
    
    cotefe.application.operations.dumbList=[];
    var arr=JSON.parse(sessionStorage.getItem(cotefe.experiments.session));
    for(i=0;i<arr.length;i++)
    {
        obj=JSON.parse(arr[i]);
        cotefe.application.operations.dumbList.push(obj)
    };
    data={
            headings:['Experiment Name','Project','Date','Edit','Delete'],
            objects :cotefe.application.operations.dumbList,
            type:"experiments",
            row:ui.make.numberOfItem
         };
    tableexp= new EJS({url: '../templates/tableModel.ejs'}).render(data);
    
    
    
    
    data={ imagedata:menu,projecttable:table,exptable:tableexp};
    
          
    
    /*
     * render jobs
     */
    /*
     * render images
     */
    completepage = new EJS({url: '../templates/dashboard.ejs'}).render(data);
    $("#content").hide().html(completepage).fadeIn("slow");     
    
    $(document).bind("load",ui.events.dashboard());
	
};
ui.make.displayProjectList=function()
{
	cotefe.application.operations.dumbList=[];
    var arr=JSON.parse(sessionStorage.getItem(cotefe.projects.session));
   
    for(i=0;i<arr.length;i++)
    {
        obj=JSON.parse(arr[i]);
        cotefe.application.operations.dumbList.push(obj)
    };
    row=arr.length;
    data={
            headings:['Project Name','Date','Edit','Delete'],
            objects :cotefe.application.operations.dumbList,
            type:"projects",
            row:row
         };
    table= new EJS({url: '../templates/tableModel.ejs'}).render(data);
    
    data={tablecontent:table,imlink:"projects"};
    projlist= new EJS({url: '../templates/projectList.ejs'}).render(data);
    $("#content").hide().html(projlist).fadeIn("slow");
    $(document).bind("load",ui.events.dashboard());
}

ui.make.displayExpList=function()
{
    cotefe.application.operations.dumbList=[];
    var arr=JSON.parse(sessionStorage.getItem(cotefe.experiments.session));
   
    for(i=0;i<arr.length;i++)
    {
        obj=JSON.parse(arr[i]);
        cotefe.application.operations.dumbList.push(obj)
    };
    row=arr.length;
    data={
            headings:['Experiment Name','Project','Date','Edit','Delete'],
            objects :cotefe.application.operations.dumbList,
            type:"experiments",
            
            row:row
         };
    table= new EJS({url: '../templates/tableModel.ejs'}).render(data);
    
    data={tablecontent:table,imlink:"experiments"};
    projlist= new EJS({url: '../templates/projectList.ejs'}).render(data);
    $("#content").hide().html(projlist).fadeIn("slow");
    $(document).bind("load",ui.events.dashboard());
};




ui.make.editNewDeleteItem		=function(params)
{
	
	if(params.method===undefined)
	{
		
		data=params.templateVars;
		if(params.id==="experiments")
			{
				data.projects=JSON.parse(sessionStorage.getItem(cotefe.projects.session));
			}
		
		completepage = new EJS({url: ('../templates/'+params.template)}).render(data);
		$("#content").hide().html(completepage).fadeIn("slow",function(){ui.events.submit();});
		
	}
	else if(params.method==="edit")
	{		
		switch(params.id)
		{
			case ui.projects.id:ui.projects.templateVars.uri=params.uri;
							 	temp=(cotefe.session.FindItemByUri(cotefe.projects.session,params.uri));
							 	ui.projects.templateVars.name=temp.name;
							 	ui.projects.templateVars.description=temp.description;
							 	data= ui.projects.templateVars;
							 	completepage = new EJS({url: ('../templates/'+ui.projects.template)}).render(data);
							 	$("#content").hide().html(completepage).fadeIn("slow",function(){ui.events.submit();});
							 	
							 	ui.projects.templateVars.uri="";							 	
							 	ui.projects.templateVars.name="";
							 	ui.projects.templateVars.description="";
							 	break;
			case ui.experiments.id:
			                    ui.experiments.templateVars.uri=params.uri;
                                temp=(cotefe.session.FindItemByUri(cotefe.experiments.session,params.uri));
                                ui.experiments.templateVars.name=temp.name;
                                ui.experiments.templateVars.description=temp.description;
                                data= ui.experiments.templateVars;
                                data.projects=JSON.parse(sessionStorage.getItem(cotefe.projects.session));
                                data.selected=temp.project;
                               
                                completepage = new EJS({url: ('../templates/'+ui.experiments.template)}).render(data);
                                $("#content").hide().html(completepage).fadeIn("slow",function(){ui.events.submit();});
                                
                                ui.experiments.templateVars.uri="";                                
                                ui.experiments.templateVars.name="";
                                ui.experiments.templateVars.description="";
                                break;
		}
	}
	else if(params.method==="delete")
	{
		params.head={method:"DELETE",uri:params.uri};
		cotefe.application.createUpdateResource(params);
	}
};
ui.make.createUpdateResource=function(json)
{
	
	cotefe.application.createUpdateResource({data:json});
}

ui.make.customAlert = function(data){
    
    
    if(data.res==="success")
    {
         var datar={classname:"alertSuccess",message:data.data};
         if(data.params.remove!=undefined)
         {
             $("a[href='"+data.params.remove+"']").parent().parent().fadeOut(500, function() { $(this).remove(); });
         }
         
    }
    else if(data.res==="fail")
    {
        
         var datar={classname:"alertFail",message:data.data};    
    }
   
    alert = new EJS({url: '../templates/alert.ejs'}).render(datar);
    $("#content").append(alert).fadeIn("slow",function(){$("#alert").delay(2000).fadeOut("slow");});  
};








