<?php

include_once 'scripts/functions.php';
//include_once 'openid/check.php';
$ex_id=null;
if(isset($_GET) && !empty($_GET))
{
	if(isset($_GET['eid']) && !empty($_GET['eid']))
	{
		$ex_id= "id='".trim($_GET['eid'])."'";
	}
	else 
	{
		$ex_id= "";
	}
}
$exp=getSingleExperiment($_GET['eid']);
$proj_id=explode('/',$exp['project']);
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="content-cype" content="text/html; charset=utf-8" />

<title>CONET Testbed Federation</title>
<link href="styles/stylesheet.css" rel="stylesheet" type="text/css" media="all" />
<script type="text/javascript" src="scripts/jquery.min.js"></script>
<script type="text/javascript" src="scripts/js/jquery-ui-1.8.14.custom.min.js"></script>

<script type="text/javascript" src="scripts/cotefev2.js"></script>
<script type="text/javascript">
$(document).ready(function() {		
	ExperimentDetails();	
 });
</script>
</head>
<body <?php echo $ex_id; ?>>

<div class="head-container">
	<div class="header-nav">
    	<div class="header-nav-container">
        	<ul>
            <li><a href="index.php" class="current-selected">Home</a></li>
            <li><a href="https://www.cooperating-objects.eu/testbed-simulation/testbed-federation/" target="_new">Documents</a></li>
            
            <li><a href=" mailto:admin@cotefe.net">Contact</a></li>
            </ul>
        </div>
        <div id="progressbar"><img src="images/ajax-loader.gif"/><div id="progressMsg"></div></div>
    
    <!--header menu ends here--></div>
    <div class="logo-container">
    	
    <!--header logo ends here--></div>
<!-- end .head-container --></div>
<div class="body-container">
	<div class="column-left">
    	<h3>Dashboard</h3>
        <hr />
        <table class="left-nav">				
					<tr><td><a href="dashboard.php">Projects</a></td></tr>
					<tr><td><a href="experiments.php?pid=<?php echo $proj_id[4]?>" class="current-selected">Experiments</a></td></tr>	
					
					<tr><td><a href="testbed.php" id="explore_testbed">Explore Testbeds</a></td></tr>														
					<tr><td><a href="<?php echo ROOTURL."/testbeds-find" ?>" id="find_testbed">Find Testbed</a></td></tr>	
		</table>
    </div>
   	
    <div class="column-right">
    	<h3>Welcome to CONET Testbed Federation</h3>
        <hr />
        <div id="breadcrumb"><?php echo $exp['name']; ?></div>
        	<div id="content">
                    <ul id="drop-down">
                      <li><a href="#">PropertySet</a>
                      	<ul id="property-set-tab">
                          <li><a href="<?php echo ROOTURL."/experiments/".$_GET['eid']."/property-sets" ?>" class="drop-down-bottom" id="create_new_property_set">Add PropertySet</a></li>                         
                        </ul>
                      </li>
                      <li><a href="#">Virtual Node Group</a>
                        <ul id="virtual-node-group-tab">
                          <li><a href="#" class="drop-down-bottom">Add Virtual Node Group</a></li>
                          
                        </ul>
                      </li>
                      <li><a href="#">Images</a>
                        <ul id="images-tab">
                          <li><a href="#" class="drop-down-bottom">Upload Image</a></li>
                         
                        </ul>
                      </li>
                      <li><a href="#">Virtual Task</a>
                      	<ul id="virtual-task-tab">
                          <li><a href="#" class="drop-down-bottom">Add Task</a></li>
                          
                        </ul>
                      </li>
                    </ul>
                    
            </div>
            <div class="clean-float"></div>
            <div id="editingfield" style="margin-top:60px;">
           			<ul class="tabs">
                        <li><a href="#tab1">Add/Edit Properties</a></li>
                        <li><a href="#tab2">Raw Json</a></li>
                    </ul>
                    
                	<div class="tab_container">
                        <div id="tab1" class="tab_content">
                            <!--Content-->
                        </div>
                        <div id="tab2" class="tab_content">
                           <!--Content-->
                        </div>
                    </div>
                    
                    <!--editingfield ends hier-->
            </div>
            <div class="clean-float"></div>
    </div>
    <div class="clean-float"></div>
<!--the .body-container ends--></div>
	<hr style="margin:0px;" />
	<div class="copyright"><span>&copy;2011 Conet Testbed Federation</span></div>
</body>
</html>