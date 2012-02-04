/*
 * checks for token saves in session and redirects to dashboard
 */

var address=document.location.href;

var session = function(access_token,token_type,exp,userinfo){
	this.access_token=access_token;
	this.token_type=token_type;
	this.exp=exp;
	this.userinfo=userinfo;
}

// check url for any session
var access_token=new Uri(address).getQueryParamValue('access_token');
if(access_token!=undefined || access_token!="")
{
	var token_type=new Uri(address).getQueryParamValue('token_type');
	var exp=new Uri(address).getQueryParamValue('expires_in');
	var temp=new session(access_token,token_type,exp,"");
	localStorage.setItem('cotefeSessionObj',JSON.stringify(temp));
	
}

var retrievedObject = JSON.parse(localStorage.getItem('cotefeSessionObj'));
if(retrievedObject.access_token)
{
	window.location.href="/htmls/getdata.html";
}
else
{

}

