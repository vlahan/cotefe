<?php
session_start();
//print_r($_POST);
if(isset($_POST) && !empty($_POST))
{
	if(isset($_POST['username']) && isset($_POST['password']))
	{
		if(trim($_POST['username'])=="conet" && trim($_POST['password'])=="password")
		{
			$host  = $_SERVER['HTTP_HOST'];
			//$uri   = rtrim(dirname($_SERVER['PHP_SELF']), '/\\');
			$uri='tu';
			$extra = 'dashboard.php';
			$_SESSION["session"]=session_id();
			$_SESSION[$_SESSION["session"]]["logged"]=1;			
			$_SESSION[$_SESSION["session"]]["name"]=trim($_POST['username']);
			header("Location: http://$host/$uri/$extra");
		}
		else
		{
			echo "False Identity ...";
		}
	}
}
else
{
	echo "No Data given";
}

?>