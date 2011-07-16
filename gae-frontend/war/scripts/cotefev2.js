// JavaScript Document


/*starts of script */

 
 
var Project=function()
{
	progressBar();
	loadProjectList();
	addEventDelete(function(){Project();});
	tabs();
	submitEvent(function(){Project();});
	
}



var Experiments=function()
{
	progressBar();
	loadExperimentsList();
	addEventDelete(function(){Experiments();});
	tabs();
	submitEvent(function(){Experiments();});
}

var PropertySets=function()
{
	progressBar();
	loadPropertySetList();
	addEventDelete(function(){PropertySets();});
	tabs();
	submitEvent(function(){PropertySets();});
}

var VirtualNodeGroup=function()
{
	progressBar();
	loadVirtualNodeGroupList();
	addEventDelete(function(){VirtualNodeGroup();});
	tabs();
	submitEvent(function(){VirtualNodeGroup();});
}

var ExperimentDetails=function()
{
	progressBar();
	createPropertyList();
	tabs();
	submitEvent(function(){ExperimentDetails();});
	
}
 
var loadProjectList=function(){
	
	var  response=sendAjax("List=project","html","#content",function(){loadFormProject();});	
}


var loadExperimentsList=function(){
	id=$('body').attr('id');
	if(id!=undefined || id!=null)
		{
			var  response=sendAjax("List=experiment&pid="+id,"html","#content",function(){loadFormProject();});	
		}
	else
		{
			var  response=sendAjax("List=experiment","html","#content",function(){loadFormProject();});	
		}
}



var loadPropertySetList=function()
{
	var response=sendAjax("List=property-sets","html","#content",function(){loadFormProject();});	
}

var loadVirtualNodeGroupList=function()
{
	var response=sendAjax("List=virtual-nodegroups","html","#content",function(){loadFormProject();});	
}


var createPropertyList=function(){

	id=$('body').attr('id');
	if(id!=undefined || id!=null)
	{
		var response=sendAjax("List=properties&pid="+id,"html","#content",function(){loadFormProject();});	
	}
	else
	{
		var response=sendAjax("List=properties","html","#content",function(){loadFormProject();});	
	}
	
}

var loadFormProject=function(){
	
	$('a[class=edit],#create_new_project,#create_new_exp,#create_new_property_set,#create_new_virtual_node_group,#upload_new_image').die('click');
	$('a[class=edit],#create_new_project,#create_new_exp,#create_new_property_set,#create_new_virtual_node_group,#upload_new_image').live('click',function(event)
			{event.preventDefault();event.stopPropagation();		
				var link=$(this).attr('href');
				id=$('body').attr('id');
				if(id!=undefined || id!=null)
					{
						var response=sendAjax("Update="+link+"&pid="+id,null,null,function (arg){onFormEvent(link,arg);});	
						
					}
				else
				{var response=sendAjax("Update="+link,null,null,function (arg){onFormEvent(link,arg);});	}
				
			});
		
		$('.item-edit').die('click');
		$('.item-edit').live('click',function(event)
			{event.preventDefault();event.stopPropagation();		
				
				var link=$(this).attr('href');
				id=$('body').attr('id');
				if(id!=undefined || id!=null)
					{
						
						var response=sendAjax("Update="+link+"&pid="+id,null,null,function (arg){onFormEvent(link,arg);});							
					}
				else
				{var response=sendAjax("Update="+link,null,null,function (arg){onFormEvent(link,arg);});	}
				
			});
	 }
var onFormEvent=function(elem,response)//getting event after ajax responds for update click
{
	
	 if(response!=false)
	{
		$('#tab1').html(response);
		/*
		 * for testbed explore
		 */
		$("ul.tabs li").removeClass("active");
		$(".tab_content").hide(); //Hide all content
		$("ul.tabs li:first").addClass("active").show(); //Activate first tab
		$(".tab_content:first").show(); //Show first tab content
		
		/*
		 * for node dragg and run
		 */
		//$('#nodesource li').bind('click',function(){alert('hey');});
		
		var Ergebnis = elem.search(/virtual-nodegroups/);
		if (Ergebnis != -1)
			{selectable_node();}
		/*
		 * node drag event ends here;
		 */
	}
}
 
var selectable_node= function()
{
	$('#nodesource').selectable({ filter:".available",
		create:function()
					{
						var emp=$("#nodeselected").is(":empty");
						if(!emp)
							{
								$(".node-legends li").each(function(){
								nos=$('#nodeselected li[title=\"'+this.title+'\"]').size();
								$("#nos_selected_node").append('<li style="padding:0.4em;">'+nos+'</li>');
						      });
							}
					},
		stop: function() {
			var result = $( "#nodeselected" ).empty();
			$( ".ui-selected", this ).each(function() {
				var index = $( "#nodesource li" ).index( this );
				id=$("ol li:nth-child("+(index+1)+")").attr('id');
				title=$("ol li:nth-child("+(index+1)+")").attr('title');
				color=$("ol li:nth-child("+(index+1)+")").css('background-color');
				result.append('<li class="node" id="'+id+'" style="background-color:'+color+';" title="'+title+'" ></li>');
			});
			$( "#nos_selected_node" ).empty();
			$(".node-legends li").each(function(){
				nos=$('#nodeselected li[title=\"'+this.title+'\"]').size();
				$("#nos_selected_node").append('<li style="padding:0.4em;">'+nos+'</li>');
		      });
		}
	});
}
var submitEvent=function(List)
{
	$('.submitP').die('click');
	$('.submitP').live('click',function(e)
		{
			e.preventDefault();e.stopPropagation();
			if($("input[name='form-type']").val()=='VNG' || $("input[name='form-type']").val()=='VNGUPDATE')
			{
				ids='';
				$('#nodeselected li').each(function(index) {
				    ids=ids+($(this).attr('id')+',');
				  });
				ids_send=ids;
				alert("Submit=form&"+($('form').serialize())+'&'+'virtual_nodes='+ids_send);
				var response=sendAjax("Submit=form&"+($('form').serialize())+'&'+'virtual_nodes='+ids_send,'append','#content',function (arg){OnSubmitFinish(arg,function(){List();});});
			}
			else
			{
				var response=sendAjax("Submit=form&"+($('form').serialize()),null,null,function (arg){;OnSubmitFinish(arg,function(){List();});});
				
			}
			
			
		});
}

var OnSubmitFinish=function(response,callback){
	if(response!=false)
		{
			if(response=='201' || response=='200')
			   {
			    
				var isfun=jQuery.isFunction(callback);
					  	if(isfun==true)
					  		{callback();}
					  	
					  
				
			   }
		   else
			   {
			   	//messageGenerate('.error_message',"There was an error : "+response);
			   }
		  
		    var isfun=jQuery.isFunction(callback);
					  	if(isfun==true)
					  		{callback();}
		}
	else
		{
			var isfun=jQuery.isFunction(callback);
					  	if(isfun==true)
					  		{callback();}
		}
	
}
 
 /*delete a item uses this live event every time its name is always deleteproject for exp and all others too*/
var addEventDelete=function(callback)
{
	$("a[class=deleteProject]").die('click');
	$("a[class=deleteProject]").live('click', function(e) 
		{e.preventDefault();e.stopPropagation();
		 	var project_link=$(this).attr('href');
		 	var response=sendAjax("Delete="+project_link,null,null,function (arg){addDeleteEvent(arg,function(){callback()});});
		 
		});
}
 
 
var addDeleteEvent=function(response,callback)
{
	if(response!=false || response=='200')
	{
		var isfun=jQuery.isFunction(callback);
					  	if(isfun==true)
					  		{callback();}
	}
	else
	{	
		
	}
}
 
 /*all ajax calls this function */
var progressBar=function ()
{
	
	$("#progressbar").ajaxStart(function(){
		   $(this).css('display','block'); 
		 }).ajaxStop(function(){
		   $(this).css('display','none'); 
		 });
}

var sendAjax=function(data,responseEvent,place,func)
{
	$.ajax({
		   type: "POST",
		   url: "scripts/operate.php",
		   data: data,
		   success:function(response, status, xhr){
			   
			   if (status == "error") {
				    var msg = "Sorry but there was an error: ";			    
				    alert('.error_message',msg + xhr.status + " " + xhr.statusText);				    
				    return false;
			  }
			  else
			  {
				  switch(responseEvent)
				  {
				  	case 'html':$(place).html(response);break;
				  	case 'append':$(place).append(response); break;				  
				  }
				  if(func!=false || func !=null)
					  {
					  	
					  	var isfun=jQuery.isFunction(func);
					  	if(isfun==true)
					  		{func(response);}
					  	
					  }
			  }
			   
		   }
		  
		 });
}

var tabs=function()
{
	$(".tab_content").empty();
	$(".tab_content").hide(); //Hide all content
	$("ul.tabs li:first").addClass("active").show(); //Activate first tab
	$(".tab_content:first").show(); //Show first tab content

	//On Click Event
	$("ul.tabs li").click(function(event) {
		event.preventDefault();event.stopPropagation();
		$("ul.tabs li").removeClass("active"); //Remove any "active" class
		$(this).addClass("active"); //Add "active" class to selected tab
		$(".tab_content").hide(); //Hide all tab content

		var activeTab = $(this).find("a").attr("href"); //Find the href attribute value to identify the active tab + content
		$(activeTab).css('display','block'); //Fade in the active ID content
		
	});
}

/**intable sliding effect*/
var loadtestbeds=function(){
    
    //$("#expandable-table").jExpand();
	
    $("#expandable-table tr:odd").addClass("odd");
    $("#expandable-table tr:odd").css("cursor","pointer");
    $("#expandable-table tr:not(.odd)").hide();
    $("#expandable-table tr:first-child").show();
    $("#expandable-table tr.odd").click(function(){
        $(this).next("tr").toggle();
        $(this).find(".arrow").toggleClass("up");
    });
    


}

