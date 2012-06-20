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