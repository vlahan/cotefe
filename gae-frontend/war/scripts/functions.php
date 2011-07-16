<?php
/*
 * start of session of new user
 */
session_start();

/*
 * called in everypage for checking user validity
 */

//define("ROOTURL", "http://localhost:8081");
//define("ROOTURL", "https://conet-testbed-federation.appspot.com");
define("ROOTURL", "http://api.cotefe.net");


include_once 'class/Form.class.php';

function checkLogged()
{
	if(isset($_SESSION[$_SESSION["session"]]["logged"]) && $_SESSION[$_SESSION["session"]]["logged"]==1)
	{
		
	}
	else 
	{
		$host  = $_SERVER['HTTP_HOST'];
		$uri   = rtrim(dirname($_SERVER['PHP_SELF']), '/\\');
		$extra = 'index.php';
		header("Location: http://$host$uri/$extra");
	}
}

/*
 * project functions
 */
function FollowProject()
{
	$root=json_decode(getUrl(ROOTURL),TRUE);
    //project list
    $projects=json_decode(getUrl($root["projects"]),TRUE);	
    return $projects;
}
/*
 * gets one project info at a time
 */

/*function getProjectInfo($url)
{
	$html=RESTUrl($url,'GET',0);
    return $html;
}*/
/*
 * form templating 
 */
function CreateProjectForm($url)
{
	if(empty($url))
	{
		/*
		 * create new form 
		 */
		$html='';
		$html.=Form::Header('New Project');
		$html.="<hr/>";
		$html.=Form::FormStart();
		$html.=HiddenField::HiddeBox('form-type','project');
		$html.=TextField::TextBox('Project Name : ','name', '');
		$html.=Description::DescriptionField('Project Description : ', "");
		$html.=Form::FromSubmit('Add Project');
		$html.=Form::FormEnd();
		return $html;
	}
	else
	{
		$resource=getUrl($url);
		$obj=json_decode($resource, true);
		$html='';
		$html.=Form::Header('Update Project');
		$html.="<hr/>";
		$html.=Form::FormStart();
		$html.=HiddenField::HiddeBox('form-type','projectUpdate');
		$html.=HiddenField::HiddeBox('uri',$obj['uri']);
		$html.=TextField::TextBox('Project Name : ','name', $obj['name']);
		$html.=Description::DescriptionField('Project Description : ',  $obj['description']);
		$html.=Form::FromSubmit('Update Project');
		$html.=Form::FormEnd();
		return $html;
	}
}
/*
 * get project List for experiment
 */
function getProjectList()
{
	$arr=null;
	$projects=FollowProject();
	if(!empty($projects))
	{
		foreach ($projects as $project)
		{
			$project_info=$project;
			$arr[$project_info['id']]=$project_info['name'];
		}
	}
	else
	{
		return null;
	}
	return $arr;
}

/*
 * project function ends
 */

/*
 * experiment functions
 */
function FollowExperiment($pid)
{
	if($pid==null)
	{
		$root=json_decode(getUrl(ROOTURL),TRUE);
		$projects=json_decode(getUrl($root["experiments"]),TRUE);
    	return $projects;
	}
    else
    {
    	$root=json_decode(getUrl(ROOTURL.'/projects/'.$pid),TRUE);    	
    	return $root["experiments"];
    }
}
function CreateExperimentForm($url)
{
	if(getProjectList()!=null)
	{
		if(empty($url))
		{
			/*
			 * create new form 
			 */
			$html='';
			$html.=Form::Header('New Experiment');
			$html.="<hr/>";
			$html.=Form::FormStart();
			$html.=HiddenField::HiddeBox('form-type','experiment');
			$html.=TextField::TextBox('Experiment Name : ','name', '');
			$html.=Description::DescriptionField('Experiment Description : ', "");
			//$html.=ListSelector::ListSelectorField('Project List:', 'project',getProjectList(),'');
			$html.=HiddenField::HiddeBox('project',$_POST['pid']);
			$html.=Form::FromSubmit('Add Experiment');
			$html.=Form::FormEnd();
			return $html;
		}
		else
		{
			$resource=getUrl($url);
			$obj=json_decode($resource, true);
			$html='';
			$html.=Form::Header('Update Experiment');
			$html.="<hr/>";
			$html.=Form::FormStart();
			$html.=HiddenField::HiddeBox('form-type','experimentUpdate');
			$html.=HiddenField::HiddeBox('uri',$obj['uri']);
			$html.=TextField::TextBox('Experiment Name : ','name', $obj['name']);
			$html.=Description::DescriptionField('Experiment Description : ',  $obj['description']);
			$prj=json_decode(getUrl($obj['project']),TRUE);
			$html.=ListSelector::ListSelectorField('Project List:', 'project',getProjectList(),$prj['id']);
			$html.=Form::FromSubmit('Update Experiement');
			$html.=Form::FormEnd();
			return $html;
		}
	}
	else
	{
		return "No Projects Found! Please create a project.";
	}
}
function getExperimentList()
{
	$arr=null;
	$experiments=FollowExperiment();
	if(!empty($experiments))
	{
		foreach ($experiments as $experiment)
		{			
			$experiment_info=json_decode(getUrl($experiment['uri']),TRUE);
			$arr[$experiment_info['id']]=$experiment_info['name'];
		}
	}
	else
	{
		return null;
	}
	return $arr;
}
function getSingleExperiment($id)
{
	$experiment_info=json_decode(getUrl(ROOTURL.'/experiments/'.$id),TRUE);
	return $experiment_info;
}
/*
 * experiment functions ends
 */

/*
 * deletes any resource as per link
 */
function deleteResource($uri)
{
	$result=RESTUrl(trim($uri), "DELETE", 0);
	return $result['code'];
}



/*
 * propertyset
 */
function FollowPropertySets()
{
	$root=json_decode(getUrl(ROOTURL),TRUE);
	$property_sets=json_decode(getUrl($root["property_sets"]),TRUE);
    return $property_sets;
}
function getSinglePropertySet($url)
{
	$property_sets=json_decode(getUrl($url),TRUE);
    return $property_sets;
}
function CreatePropertySetForm($url,$eid)
{
		if(empty($url))
		{
			/*
			 * create new form 
			 */
			$html='';
			$html.=Form::Header('New PropertySet');
			$html.="<hr/>";
			$html.=Form::FormStart();
			$html.=HiddenField::HiddeBox('form-type','property-set');
			$html.=HiddenField::HiddeBox('experiment',$eid);
			$html.=TextField::TextBox('PropertySet Name : ','name', '');
			$html.=Description::DescriptionField('PropertySet Description : ', "");
			//$html.=ListSelector::ListSelectorField('Select an Experiment :', 'experiment',getExperimentList($eid),'');
			
			$html.=ListSelector::ListSelectorField('Select a Platform :', 'platform',getPlatformsList(),'');
			$html.=TextField::TextBox('Nr. of Node : ','node_count', '');
			$html.=Form::FromSubmit('Add PropertySet');
			$html.=Form::FormEnd();
			return $html;
		}
		else
		{
			$resource=getUrl($url);
			$obj=json_decode($resource, true);
			$html='';
			$html.=Form::Header('Update PropertySet');
			$html.="<hr/>";
			$html.=Form::FormStart();
			$html.=HiddenField::HiddeBox('form-type','property-setUpdate');
			$html.=HiddenField::HiddeBox('uri',$obj['uri']);
			$html.=TextField::TextBox('PropertySet Name : ','name', $obj['name']);
			$html.=Description::DescriptionField('PropertySet Description : ', $obj['description']);
			$experiment=json_decode(getUrl($obj['experiment']),TRUE);
			$html.=ListSelector::ListSelectorField('Select an Experiment :', 'experiment',getExperimentList(),$experiment['id']);
			$platform=json_decode(getUrl($obj['platform']),TRUE);
			$html.=ListSelector::ListSelectorField('Select a Platform :', 'platform',getPlatformsList(),$platform['id']);
			$html.=TextField::TextBox('Nr. of Node : ','node_count', $obj['node_count']);
			//$html.=Form::FromSubmit('Add PropertySet');
			$html.=Form::FormEnd();
			return $html;
		}
	
	
}
function FollowVirtualNode()
{
	$root=json_decode(getUrl(ROOTURL),TRUE);
	
	$virtual_nodes=json_decode(getUrl($root["virtual_nodes"]),TRUE);
	
    return $virtual_nodes;
}
function getVirtualNodeList($params)
{
	$arr=null;
	$VirtualNodes=FollowVirtualNode();
	
	if(!empty($VirtualNodes))
	{
		if($params=='count')
		{
			return count($VirtualNodes);
		}
		$c=0;
		
		foreach ($VirtualNodes as $VirtualNode)
		{			
			$arr[$c]['id']=$VirtualNode['id'];
			$arr[$c]['name']=$VirtualNode['name'];
			
			$arr[$c]['property_set_id']=$VirtualNode['property_set'];
			$c++;
		}
		
	}
	else
	{
		return null;
	}
	return $arr;
}
/*
 * propertysets ends
 */


/*
 * virtual node group
 */
function FollowVirtualNodeGroup()
{
	$root=json_decode(getUrl(ROOTURL),TRUE);
	$virtual_nodegroups=json_decode(getUrl($root["virtual_nodegroups"]),TRUE);
    return $virtual_nodegroups;
}
function CreateVNGForm($url)
{
	if(getExperimentList()!=null)
	{
		$node_num=getVirtualNodeList(null);
		if(count($node_num)!=null)
		{
			if(empty($url))
			{
				$html='';
				$html.=Form::Header('New Virtual Node Group');
				$html.="<hr/>";
				$html.=Form::FormStart();
				$html.=HiddenField::HiddeBox('form-type','VNG');
				$html.=TextField::TextBox('Virtual Node Group Name : ','name', '');
				$html.=Description::DescriptionField('Virtual Node Group Description : ', "");
				$html.=ListSelector::ListSelectorField('Select an Experiment :', 'experiment',getExperimentList(),'');
				
				//get total VNG
				$node_pack="<ol id='nodesource' class='ui-selected' >";
				$no_of_nodes=count($node_num);
				$node_array=$node_num;
				
				$propertyset=array();
				for($i=0;$i<$no_of_nodes;$i++)
				{
						$propertyset[]=$node_array[$i]['property_set_id'];
				}
				$unique_propertyset_values=array_unique($propertyset);
				//create key and style
				$style=array();
				$colorcounter=0;
				foreach($unique_propertyset_values as $unique_propertyset_value)
				{
					$style[$unique_propertyset_value]=random_color();
					$colorcounter++;					
				}			
				
				foreach($node_array as $c=>$key) {
			        $sort_numcie[] = $key['property_set_id'];
			        
			    }
				
				array_multisort( $sort_numcie,SORT_DESC,$node_array);
				for($i=0;$i<$no_of_nodes;$i++)
				{
					$node_pack.="<li class='node available' id=".$node_array[$i]['id']." style='background:#".$style[$node_array[$i]['property_set_id']].";' title=\"".$node_array[$i]['property_set_id']."\" ></li>";
				}
				$node_pack.="</ol>";
				//getting total VNG Ends
				
				$html.=EmptyTR::EmptyTableTR('Select Node by Mouse Dragging on box below:<br>'.$node_pack, 'Selected Nodes: <br><ol id="nodeselected"></ol>');
				//color legend
				$colorlegend="<ol class='node-legends'>";
				foreach($style as $key=>$value)
				{
					$propertySetSingle=getSinglePropertySet($key);
					$colorlegend.="<li style='background:#".$value."' title=\"".$key."\"><span>".$propertySetSingle['name']."</span></li>";
				}
				$colorlegend.="</ol>";
				$html.=EmptyTR::EmptyTableTR('Color Legends:<br>'.$colorlegend, 'You have selected :<ol id="nos_selected_node"></ol>');
				$html.=Form::FromSubmit('Save Virtual Node Group');
				$html.=Form::FormEnd();
				return $html;
			}
			else
			{
				$resource=getUrl($url);
				$obj=json_decode($resource, true);
				$html='';
				$html.=Form::Header('Update Virtual Node Group');
				$html.="<hr/>";
				$html.=Form::FormStart();
				$html.=HiddenField::HiddeBox('form-type','VNG');
				$html.=TextField::TextBox('Virtual Node Group Name : ','name', $obj['name']);
				$html.=Description::DescriptionField('Virtual Node Group Description : ', $obj['description']);
				$experiment=json_decode(getUrl($obj['experiment']),TRUE);
				$html.=ListSelector::ListSelectorField('Select an Experiment :', 'experiment',getExperimentList(),$experiment['id']);
				
				//get total VNG
				$node_pack="<ol id='nodesource' class='ui-selected' >";
				$no_of_nodes=getVirtualNodeList('count');
				$node_array=getVirtualNodeList(null);
				
				$propertyset=array();
				for($i=0;$i<$no_of_nodes;$i++)
				{
						$propertyset[]=$node_array[$i]['property_set_id'];
				}
				$unique_propertyset_values=array_unique($propertyset);
				//create key and style
				$style=array();
				$colorcounter=0;
				foreach($unique_propertyset_values as $unique_propertyset_value)
				{
					$style[$unique_propertyset_value]=random_color();
					$colorcounter++;					
				}			
				
				foreach($node_array as $c=>$key) {
			        $sort_numcie[] = $key['property_set_id'];
			        
			    }
				
				array_multisort( $sort_numcie,SORT_DESC,$node_array);
				for($i=0;$i<$no_of_nodes;$i++)
				{
					$node_pack.="<li class='node available' id=".$node_array[$i]['id']." style='background:#".$style[$node_array[$i]['property_set_id']].";' title=\"".$node_array[$i]['property_set_id']."\" ></li>";
				}
				$node_pack.="</ol>";
								
				/*
				 * for already selected node
				 */
				
				$nodes_already_in=$obj['virtual_nodes'];
				foreach($nodes_already_in as $c=>$key) {
			        $sort_numcie1[] = $key['property_set'];
			        
			    }
			    array_multisort( $sort_numcie1,SORT_DESC,$nodes_already_in);
				$already_nodes="";
				foreach ($nodes_already_in as $node)
				{
					$already_nodes.="<li class='node available' id=".$node['id']." style='background:#".$style[$node['property_set']].";' title='".$node['property_set']."' ></li>";;
				}
				
				//getting total VNG Ends
				
				$html.=EmptyTR::EmptyTableTR('Select Node by Mouse Dragging on box below:<br>'.$node_pack, 'Selected Nodes: <br><ol id="nodeselected">'.$already_nodes.'</ol>');
				//color legend
				$colorlegend="<ol class='node-legends'>";
				foreach($style as $key=>$value)
				{
					$propertySetSingle=getSinglePropertySet($key);
					$colorlegend.="<li style='background:#".$value."' title=\"".$key."\"><span>".$propertySetSingle['name']."</span></li>";
				}
				$colorlegend.="</ol>";
				
				
				
				$html.=EmptyTR::EmptyTableTR('Color Legends:<br>'.$colorlegend, 'You have selected :<ol id="nos_selected_node"></ol>');
				$html.=Form::FromSubmit('Update Virtual Node Group');
				$html.=Form::FormEnd();
				return $html;
			}
		}
		else
		{
			echo "No Nodes Found! Please Create Nodes first.";
			return null;
		}
	}
	else
	{
		echo "No Experiment Found! Please Create Experiment.";
	}
}
function random_color(){
    mt_srand((double)microtime()*1000000);
    $c = '';
    while(strlen($c)<6){
        $c .= sprintf("%02X", mt_rand(0, 255));
    }
    return $c;
	//return dechex(rand(0,10000000));
}
function getVirtualNodeGroupList($params)
{
	$arr=null;
	$VirtualNodeGroups=FollowVirtualNodeGroup();
	if(!empty($VirtualNodeGroups))
	{
		if($params=='count')
		{
			return count($VirtualNodeGroups);
		}
		
		foreach ($VirtualNodeGroups as $VirtualNodeGroup)
		{			
			$experiment_info=json_decode(getUrl($VirtualNodeGroup['uri']),TRUE);
			$arr[$experiment_info['id']]=$experiment_info['name'];
		}
	}
	else
	{
		return null;
	}
	return $arr;
}
/*
 * virtual node group ends
 */

/*
 * images
 */
function FollowImages($experimentpath)
{
	//$root=json_decode(getUrl(ROOTURL),TRUE);
	$virtual_nodegroups=json_decode(getUrl($experimentpath.'/images'),TRUE);
    return $images;
}
function createImageList($experimentPath)
{
	/*
	 * get image list in an experiment
	 */
}
/*
 * images ends
 */

/*
 * platforms
 */
function FollowTestBeds()
{
	$root=json_decode(getUrl(ROOTURL),TRUE);
	$virtual_nodegroups=json_decode(getUrl($root["testbeds"]),TRUE);
    return $virtual_nodegroups;
}
/*
 * platfomr ends
 */


/*
 * get platform 
 */
function FollowPlatform()
{
	$root=json_decode(getUrl(ROOTURL),TRUE);
    //project list
    $platforms=json_decode(getUrl($root["platforms"]),TRUE);	
    return $platforms;
}
function getPlatformsList()
{
	$arr=null;
	$platforms=FollowPlatform();
	if(!empty($platforms))
	{
		foreach ($platforms as $platform)
		{
			$platform_info=json_decode(getUrl($platform['uri']),TRUE);
			$arr[$platform_info['id']]=$platform_info['name'];
		}
	}
	else
	{
		return null;
	}
	return $arr;
}
/*
 * gettign platform ends 
 */

function getUrl($url)
{  	
	$html=RESTUrl($url,'GET',0);
    return getResponse($html);
}
/*
 * givs response code back
 */
function getResponseCode($response)
{
	return $response['code'];
}
/*
 * givs only response text back
 */
function getResponse($response)
{
	return $response['response'];
}

/*
 * does all the restful calls and returns row data back with response code
 */
function RESTUrl($url,$method,$data)
{
	
	if( !ini_get('safe_mode') ){ 
            set_time_limit(45); 
      } 
	$headers = array('Accept: application/json','Content-Type: application/json',);
	//$useragent="Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.1) Gecko/20061204 Firefox/2.0.0.1";
	$useragent="cotefe.minds.website";
	
	$handle = curl_init();
	curl_setopt($handle, CURLOPT_URL, $url);
	curl_setopt($handle, CURLOPT_HTTPHEADER, $headers);
	curl_setopt($handle, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($handle, CURLOPT_SSL_VERIFYHOST, false);
	curl_setopt($handle, CURLOPT_SSL_VERIFYPEER, false);
	curl_setopt($handle, CURLOPT_TIMEOUT,40);
	//curl_setopt($handle, CURLOPT_USERAGENT, $useragent);

	
	switch($method)
	{
	
	case 'GET':
	break;
	
	case 'POST':
	curl_setopt($handle, CURLOPT_POST, true);
	curl_setopt($handle, CURLOPT_POSTFIELDS, $data);
	break;
	
	case 'PUT':
	curl_setopt($handle, CURLOPT_CUSTOMREQUEST, 'PUT');
	curl_setopt($handle, CURLOPT_POSTFIELDS, $data);
	break;
	
	case 'DELETE':
	curl_setopt($handle, CURLOPT_CUSTOMREQUEST, 'DELETE');
	break;
	}
		
	$response['response'] = curl_exec($handle);
	if($response['response']===false)
	{
		$response['response']="Something is wrong with Connection";
	}
	$response['code'] = curl_getinfo($handle, CURLINFO_HTTP_CODE);
	return $response;
}

/*
 * shorten string 
 */
function shortenString($str , $str_length) //get string to be shortened and length to be displayed
{
	if(strlen($str)>$str_length)
	{
		return (substr($str,0,($str_length-3))."...");
	}
	else
	{ 
		return $str;
	}
}


function urlGenerate($page,$params_n)
{
	$params   =$_SERVER['QUERY_STRING'];;
	echo $params;
	 if(empty($params))
	 	$params=$params;
	 else
	 {$params.='&'.$params_n;}
	$currentUrl = $page.'?' . $params;
	 
	return $currentUrl;
}


?>