
$(document).ready(function() {	
	var  response=sendAjax("List=project","html","#content",null);	
	addEventDelete();
 });

var createLists=function()
{
	progressBar();
	/*
	 * function starts here
	 */

	loadProjectList();
	/*loadExpList();
	loadPropertySetList();*/
	addEventDelete();
	addEventForm();
	submitEvent();
	/*
	 * function ends
	 */
	
	
	toggleMessage('.success_message');
	
}


/*
 * Message box 
 */
function messageGenerate(classname,message)
{
	 	$(classname).fadeIn('slow');
		$(classname+' span').text(message);
		$(classname+' img').click(function(){$(classname).fadeOut('slow');});
	 
}
function toggleMessage(class)
{
	 if($(class).css('display')=='block')
	  {
		 $(class).animate({opacity:"toggle"},1000,"linear", function(){ $(this).css('display','none'); });
		 
	  }
	 
}


/*
 * loading first project list and add event to buttons
 */
var loadProjectList=function(){	
	var  response=sendAjax("List=project","html","#content",function(){loadExpList();});	
}

/*
 * load experiment list
 */
var loadExpList=function(){
	var  response=sendAjax("List=experiment","append","#content",function(){loadPropertySetList();});	
}
var loadPropertySetList=function()
{
	var response=sendAjax("List=property-sets","append","#content",function(){loadVirtualNodeGroupList();});	
}
var loadVirtualNodeGroupList=function()
{
	var response=sendAjax("List=virtual-nodegroups","append","#content",null);	
}
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
    toggleMessage('.alert_message');


}

var addEventDelete=function()
{
	$("a[class=deleteProject]").die('click');
	$("a[class=deleteProject]").live('click', function(e) 
		{e.preventDefault();e.stopPropagation();
		 var project_link=$(this).attr('href');
		 var response=sendAjax("Delete="+project_link,null,null,function (arg){addDeleteEvent(arg);});
	});
}

var addDeleteEvent=function(response)
{
	if(response!=false || response=='200')
	{
		messageGenerate('.success_message','Item Successfuly deleted. Wait till we refresh List..');
		createLists();
	}
	else
	{	
		createLists();
	}
}

var addEventForm=function()
{
	$('a[class=edit],#create_new_project,#create_new_exp,#create_new_property_set,#explore_testbed').die('click');
	$('a[class=edit],#create_new_project,#create_new_exp,#create_new_property_set,#create_new_virtual_node_group').live('click',function(event)
			{event.preventDefault();event.stopPropagation();
				messageGenerate('.alert_message','Your Form Is being Created. Please wait...');
				var link=$(this).attr('href');				
				var response=sendAjax("Update="+link,null,null,function (arg){onFormEvent(arg);});				
			});
	$('#explore_testbed').live('click',function(event)
			{event.preventDefault();event.stopPropagation();
				messageGenerate('.alert_message','Your List is being generated. Please wait...');
				var link=$(this).attr('href');				
				var  response=sendAjax("List=testbeds","html","#content",function(args){loadtestbeds();});	
			});
}
var onFormEvent=function(response)//getting event after ajax responds for update click
{
	if(response!=false)
	{
		$('#content').html(response);
		$('#nodesource').selectable({ filter:".available",
			create:function()
						{
							var emp=$("#nodeselected").is(":empty");
							if(!emp)
								{
									$(".node-legends li").each(function(){
									nos=$('#nodeselected li[title='+this.title+']').size();
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
					result.append('<li class="node" id="'+id+'" style="background-color:'+color+';" title="'+title+'"></li>');
				});
				$( "#nos_selected_node" ).empty();
				$(".node-legends li").each(function(){
					nos=$('#nodeselected li[title='+this.title+']').size();
					$("#nos_selected_node").append('<li style="padding:0.4em;">'+nos+'</li>');
			      });
			}
		});
		toggleMessage('.alert_message');
	}
	else
	{
		
		createLists();
	}
}
var submitEvent=function()
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
				var response=sendAjax("Submit=form&"+($('form').serialize()),null,null,function (arg){OnSubmitFinish(arg);});
			}
		});
}


var OnSubmitFinish=function(response){
	if(response!=false)
		{
			if(response=='201' || response=='200')
			   {
			    messageGenerate('.success_message','Item Successfuly Created. Wait till we refresh List..');
			   }
		   else
			   {
			   	messageGenerate('.error_message',"There was an error : "+response);
			   }
		  
		    createLists();
		}
	else
		{
			createLists();
		}
	
}

var progressBar=function ()
{
	$("#loader").ajaxStart(function(){
		   $(this).fadeIn('slow');
		 }).ajaxStop(function(){
			  $(this).fadeOut('slow');
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