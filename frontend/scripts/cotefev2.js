// JavaScript Document


/*starts of script */
$(document).ready(function() {	
	Project();	
 });
 
 
var Project=function()
{
	progressBar();
	loadProjectList();
	addEventDelete(function(){Project();});
	tabs();
	submitEvent(function(){Project();});
	/*
	 * function ends
	 */
}
 
 
 var loadProjectList=function(){	
	var  response=sendAjax("List=project","html","#content",function(){loadFormProject();});	
}

var loadFormProject=function(){
	$('a[class=edit],#create_new_project').die('click');
	$('a[class=edit],#create_new_project').live('click',function(event)
			{event.preventDefault();event.stopPropagation();		
				var link=$(this).attr('href');			
				var response=sendAjax("Update="+link,null,null,function (arg){onFormEvent(arg);});				
			});
	 }
 var onFormEvent=function(response)//getting event after ajax responds for update click
{
	if(response!=false)
	{
		$('#tab1').html(response);
		
		$("ul.tabs li").removeClass("active");
		$(".tab_content").hide(); //Hide all content
		$("ul.tabs li:first").addClass("active").show(); //Activate first tab
		$(".tab_content:first").show(); //Show first tab content
		
	}
}
var submitEvent=function(List)
{
	$('.submitP').die('click');
	$('.submitP').live('click',function(e)
		{
			e.preventDefault();e.stopPropagation();
			if($("input[name='form-type']").val()=='VNG')
			{
				ids='';
				$('#nodeselected li').each(function(index) {
				    ids=ids+( '' + $(this).attr('id')+',');
				  });
				ids_send=(ids+'');
				var response=sendAjax("Submit=form&"+($('form').serialize())+'&'+'virtual_nodes='+ids_send,null,null,function (arg){OnSubmitFinish(arg);});
			}
			else
			{
				var response=sendAjax("Submit=form&"+($('form').serialize()),null,null,function (arg){OnSubmitFinish(arg,function(){List();});});
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
			   	messageGenerate('.error_message',"There was an error : "+response);
			   }
		  
		    Project();
		}
	else
		{
			Project();
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
				    messageGenerate('.error_message',msg + xhr.status + " " + xhr.statusText);				    
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
	$("ul.tabs li").click(function() {

		$("ul.tabs li").removeClass("active"); //Remove any "active" class
		$(this).addClass("active"); //Add "active" class to selected tab
		$(".tab_content").hide(); //Hide all tab content

		var activeTab = $(this).find("a").attr("href"); //Find the href attribute value to identify the active tab + content
		$(activeTab).css('display','block'); //Fade in the active ID content
		return false;
	});
}

/**intable sliding effect*/
var loadtestbeds=function(){
    
    //$("#expandable-table").jExpand();
    $("#table-list tr:odd").addClass("odd");
    $("#table-list tr:odd").css("cursor","pointer");
    $("#table-list tr:not(.odd)").hide();
    $("#table-list tr:first-child").show();
    $("#table-list tr.odd").click(function(){
        $(this).next("tr").toggle();
        //$(this).find(".arrow").toggleClass("up");
    });
    


}

