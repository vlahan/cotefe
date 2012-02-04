
/*
 * constants globals
 */

var apiuri="https://api.cotefe.net/";

var path = ["me",
			"projects/",
			"experiments/",
			"platforms/",
			"testbeds/",
			"jobs/"];

var tempStr="";
/*
 * make link
 */
function makeLink(path)
{
	return apiuri+path;
}

/*
 * function ajax 
 * method: GET,POST,PUT,DELETE, url,token,
 * POST,PUT json payload
 */
function ajaxFunction(method,uri,token,payload,callback)
			{
				var ajaxRequest; 
				try
				{
					ajaxRequest = new XMLHttpRequest();
				} 
				catch (e)
				{
					try
					{
						ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
					} 
					catch (e) 
					{
						try{
							ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
						} catch (e){
							alert("Your browser broke!");
							return false;
						}
					}
				}
				ajaxRequest.onreadystatechange = function(){
					if(ajaxRequest.readyState == 4 ){
						if(ajaxRequest.status==200)
						{
							if((typeof callback) == "function")
								{callback(uri,ajaxRequest.responseText);}
						}
						else
						{
							alert("there was an error");
						}
					}
				}
				
				ajaxRequest.open(method, (uri+"?access_token="+token), false);
				ajaxRequest.setRequestHeader("Content-type", "application/json")
				ajaxRequest.send(payload); 
			}
			

/*
 * json parse
 */
function jsonRep(data)
{
			return jQuery.parseJSON(data);
}

function savetoLocal(name,value){
	localStorage.setItem(name,value);
}
function getToken()
{
	var me=JSON.parse(localStorage.getItem('cotefeSessionObj'));
	if(!me)
		return null;
	else
		return me.access_token;
}

function signOut()
{
	localStorage.removeItem("cotefeMe");
	localStorage.removeItem("cotefeTestbeds");
	localStorage.removeItem("cotefePlatforms");
	localStorage.removeItem("cotefeProjects");
	localStorage.clear();
	window.location.href="../";
}


function capitalize (text) {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

function currentUser()
{
	var me=JSON.parse(localStorage.getItem('cotefeMe'));
	if(!me)
		return null;
	else
		return capitalize(me.name);
}

function getProjectList()
{
	var link=makeLink("projects/");
	ajaxFunction("GET",link,getToken(),null,getProjectListCallback)
	
}
function getProjectListCallback(uri,json)
{
	var obj= JSON.parse(json, jsonKey);
	
}
function jsonKey(key,value)
{
	if(key == "uri")
	{
		var link=value;
		ajaxFunction("GET",link,getToken(),null,sendProjectsToLocalStorage)
	}
}

function sendProjectsToLocalStorage(uri,value)
{

	var pre=localStorage.getItem("cotefeProjects");
	
	if(pre==null)
	{
		pre="";
		savetoLocal("cotefeProjects",(pre+value));
	}
	else
	{
			savetoLocal("cotefeProjects",(pre+","+value));
	}
	
}




/*
 * make json for table
 * read from session
 */

function dispProject(len,pos)
{
	var json=(localStorage.getItem("cotefeProjects"));
	json="["+json+"]";//making valid json
	var table=(makeTable(json,['uri','name','datetime_created'],['Project name','Created Date','Edit','Delete'], 'shadow-dark',len));
	if(pos==0)
		pushInUi("tab1",table);
	else
		pushInUi("tab_content",table);	
}

function getItemFromLocal(key,uri)
{
	var arr=JSON.parse(("["+localStorage.getItem(key)+"]"));
	for(i=0;i<arr.length;i++)
	{
		if(uri==arr[i].uri)
		{
			return arr[i];
		}
	}
	return null;
}

function makeTable(jsonData, keys,header, tableClassName,len)
{
	
    var tbl = "<table class='" + tableClassName + "'>";
    if(header!="" || header != null )
    {
    	tbl+="<tr>";
    	for(i=0;i<header.length;i++)
    	{
    		tbl+=("<th>"+header[i]+"</th>")
    	}
    	tbl+="</tr>";
    	var arr=JSON.parse(jsonData);
    	if(arr[0] ==null)
    	{
    		return "<tr><td>No Items you have yet!!</td><tr></table>";
    	}
    	if(len==0)
    	{
    		len=arr.length;
    	}
    	else
    	{
    		len=(len< arr.length?len:arr.length);
    	}
    	for(i=0;i<len;i++)
    	{
    		tbl+="<tr>";
    		tbl+="<td>"+arr[i].name+"</td>";
    		var mySplitResult = (arr[i].datetime_created).split("T");
    		tbl+="<td>"+mySplitResult[0]+"</td>";
    		tbl+="<td><a class='edit' href='"+arr[i].uri+"'>Edit</a></td>";
    		tbl+="<td><a class='delete' href='"+arr[i].uri+"'>Delete</a></td>";		
    		tbl+="</tr>";
    		
    	}
    	tbl+="</table>";
    }
    
    return tbl;
    
}

function pushInUi(id,data)
{
	var element=document.getElementById(id);
	element.innerHTML=data;
}
