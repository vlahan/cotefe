<?php

header('content-type: text/html');
include_once 'functions.php';

if(isset($_POST) &&  !empty($_POST) )
{
	if(isset($_POST['Home']) && $_POST['Home']=="content")
	{
		$response=getUrl(ROOTURL);
		echo $response;
	}
	elseif(isset($_POST['List']))
	{
		switch (trim($_POST['List']))
		{
			case "project": 
							$title='Your current projects:';
							$header[0]['text']='Name';
							$header[0]['attribute']='width="40%" style="text-align:left;"';
							$header[1]['text']='No. Of Experiment';
							$header[1]['attribute']='style="text-align:center;"';
							$header[2]['text']='Edit';
							$header[2]['attribute']='width="5%"';
							$header[3]['text']='Delete';
							$header[3]['attribute']='width="8%" style="padding-right:0px;"';
							
							$records=array();
							$projects=FollowProject();
							if(!empty($projects))
							{
								$i=0;
								foreach ($projects as $project)
								{
									$project_info=$project;
									
									$records[$i][0]['text']=$project_info['name'];
									$records[$i][0]['attribute']='style="padding-left:10px;"';
									$records[$i][0]['a']='experiments.php?pid='.$project_info['id'];
									$records[$i][1]['text']=$project_info['experiment_count'];
									$records[$i][1]['attribute']='style="text-align:center;"';
									$records[$i][2]['text']='<a class="edit" href="'.$project_info['uri'].'" ><img src="images/edit.png" /></a>';
									$records[$i][2]['attribute']='style="padding-left:10px;"';
									$records[$i][3]['text']='<a class="deleteProject" href="'.$project_info['uri'].'"><img src="images/close.png" /></a>';
									$records[$i][3]['attribute']='style="padding-left:20px;"';
									
									
									$i++;
								}
								$records[$i][0]['text']='<a class="add-links" href="'.ROOTURL.'/projects" " id="create_new_project" >Add New Project</a>';
								$records[$i][0]['attribute']='style="padding-left:10px;"';
								$records[$i][1]['text']=$records[$i][2]['text']=$records[$i][3]['text']='';
								$obj=new Createtable($title,$header,$records);
								
								echo $obj->render();
							}
							else
							{
								
								echo "You have no projects . Lets create One. ".'<a class="add-links" href="'.ROOTURL.'/projects" " id="create_new_project" >Add New Project</a>';
							}
						    break;
							
							
							
			case "experiment":
							$project_id=null;
							
							if(isset($_POST['pid']) && !empty($_POST['pid']))
							{
								if($_POST['pid']=="")
								{
									$project_id=null;
									$proj_info="";
								}
								else 
								{
									$project_id=$_POST['pid'];
									$proj_n=json_decode(getUrl(ROOTURL.'/projects/'.$project_id),TRUE);
									$proj_info=$proj_n['name'];
								}
								
							}
							
							$title='Your current Experiments under Project: '.$proj_info;
							$header[0]['text']='Name';
							$header[0]['attribute']='width="40%" style="text-align:left;padding-left:10px;"';
							
							$header[1]['text']='Virtual Nodes';
							$header[1]['attribute']='style="text-align:center;"';
							$header[2]['text']='Edit';
							$header[2]['attribute']='width="5%"';
							$header[3]['text']='Delete';
							$header[3]['attribute']='width="8%"';
			
							$records=array();
							$exps=FollowExperiment($project_id);
							
							if(!empty($exps))
							{
								$i=0;
								foreach ($exps as $exp)
								{
									$exp_info=$exp;
									$records[$i][0]['text']=$exp_info['name'];
									$records[$i][0]['attribute']='style="padding-left:10px;"';
									
									$records[$i][0]['a']='experimentsdetails.php?eid='.$exp_info['id'];
									$records[$i][1]['text']=$exp_info['virtual_node_count'];
									$records[$i][1]['attribute']='style="text-align:center;"';
									
									$records[$i][2]['text']='<a class="edit" href="'.$exp_info['uri'].'" ><img src="images/edit.png" /></a>';
									$records[$i][2]['attribute']='style="padding-left:10px;"';
									$records[$i][3]['text']='<a class="deleteProject" href="'.$exp_info['uri'].'"><img src="images/close.png" /></a>';
									$records[$i][3]['attribute']='style="padding-left:20px;"';
									
									
									$i++;
								}
								$records[$i][0]['text']='<a class="add-links" href="'.ROOTURL.'/experiments" " id="create_new_exp" >Add New Experiments</a>';
								$records[$i][0]['attribute']='style="padding-left:10px;"';
								$records[$i][1]['text']=$records[$i][2]['text']=$records[$i][3]['text']='';
								$obj=new Createtable($title,$header,$records);
								
								echo $obj->render();
							}
							else
							{
								
								echo "You have no Experiments . Lets create one. ".'<a class="add-links" href="'.ROOTURL.'/experiments" " id="create_new_exp" >Add New Experiments</a>';
							}
						    break;
			
			case "property-sets":
							$title='Your current property-sets:';
							$header[0]['text']='Name';
							$header[0]['attribute']='width="40%" style="text-align:left;padding-left:10px;"';
							$header[1]['text']='Experiment';
							$header[1]['attribute']='style="text-align:center;"';							
							$header[2]['text']='Platform';
							$header[2]['attribute']='style="text-align:center;"';
							$header[3]['text']='VN';
							$header[3]['attribute']='style="text-align:center;"';
							$header[4]['text']='View';
							$header[4]['attribute']='width="5%"';
							$header[5]['text']='Delete';
							$header[5]['attribute']='width="7%"';
			
							$records=array();
							$PropertySets=FollowPropertySets();
							if(!empty($PropertySets))
							{
								$i=0;
								foreach ($PropertySets as $PropertySet)
								{
									$PropertySet_info=json_decode(getUrl($PropertySet['uri']),TRUE);
									
									$records[$i][0]['text']=$PropertySet_info['name'];
									$records[$i][0]['attribute']='style="padding-left:10px;"';
									
									$experiment_info=json_decode(getUrl($PropertySet_info['experiment']),TRUE);
									$records[$i][1]['text']=$experiment_info['name'];
									
									$records[$i][1]['attribute']='style="text-align:center;"';
									$platform_info=json_decode(getUrl($PropertySet_info['platform']),TRUE);
									
									$records[$i][2]['text']=$platform_info['name'];
									$records[$i][2]['attribute']='style="text-align:center;"';
											
									$records[$i][3]['text']=$PropertySet_info['node_count'];
									$records[$i][3]['attribute']='style="text-align:center;"';
									
									$records[$i][4]['text']='<a class="edit" href="'.$PropertySet_info['uri'].'" ><img src="images/view.png" /></a>';
									$records[$i][4]['attribute']='style="padding-left:10px;"';
									$records[$i][5]['text']='<a class="deleteProject" href="'.$PropertySet_info['uri'].'"><img src="images/close.png" /></a>';
									$records[$i][5]['attribute']='style="padding-left:15px;"';
									
									
									$i++;
								}
								$records[$i][0]['text']='<a class="add-links" href="'.ROOTURL.'/property-sets" " id="create_new_property_set" >Add New Property Set</a>';
								$records[$i][0]['attribute']='style="padding-left:10px;"';
								$records[$i][1]['text']=$records[$i][2]['text']=$records[$i][3]['text']=$records[$i][4]['text']=$records[$i][5]['text']='';
								$obj=new Createtable($title,$header,$records);
								
								echo $obj->render();
							}
							else
							{
								
								echo "You have no Property Sets . Lets create one. ".'<a class="add-links" href="'.ROOTURL.'/property-sets" " id="create_new_property_set" >Add New Property Set</a>';
							}
						    break;
							
							
							
			case "virtual-nodegroups":
							$title='Your current Virtual Node Groups:';
							$header[0]['text']='Name';
							$header[0]['attribute']='width="40%" style="text-align:left;padding-left:10px;"';
							$header[1]['text']='Experiment';
							$header[1]['attribute']='style="text-align:left;"';					
							$header[2]['text']='VN';
							$header[2]['attribute']='style="text-align:center;"';
							$header[3]['text']='Edit';
							$header[3]['attribute']='width="5%"';
							$header[4]['text']='Delete';
							$header[4]['attribute']='width="7%"';
							
							$records=array();
							
							$VirtualNodeGroups=FollowVirtualNodeGroup();
							//echo "yes man ";
							
							if(!empty($VirtualNodeGroups))
							{
								$i=0;
								foreach ($VirtualNodeGroups as $VirtualNodeGroup)
								{
									$VirtualNodeGroup_info=json_decode(getUrl($VirtualNodeGroup['uri']),TRUE);
									
									$records[$i][0]['text']=$VirtualNodeGroup_info['name'];
									$records[$i][0]['attribute']='style="padding-left:10px;"';
									
									$experiment_info=json_decode(getUrl($VirtualNodeGroup_info['experiment']),TRUE);
									$records[$i][1]['text']=$experiment_info['name'];
									$records[$i][1]['attribute']='style="text-align:left;"';
											
									$records[$i][2]['text']=$VirtualNodeGroup_info['node_count'];
									$records[$i][2]['attribute']='style="text-align:center;"';
									
									$records[$i][3]['text']='<a class="edit" href="'.$VirtualNodeGroup_info['uri'].'" ><img src="images/edit.png" /></a>';
									$records[$i][3]['attribute']='style="padding-left:10px;"';
									$records[$i][4]['text']='<a class="deleteProject" href="'.$VirtualNodeGroup_info['uri'].'"><img src="images/close.png" /></a>';
									$records[$i][4]['attribute']='style="padding-left:15px;"';								
									$i++;
								}
								$records[$i][0]['text']='<a class="add-links" href="'.ROOTURL.'/virtual-nodegroups" " id="create_new_virtual_node_group" >Add New Virtual Node Group</a>';
								$records[$i][0]['attribute']='style="padding-left:10px;"';
								$records[$i][1]['text']=$records[$i][2]['text']=$records[$i][3]['text']=$records[$i][4]['text']='';
								$obj=new Createtable($title,$header,$records);
								
								echo $obj->render();
							}
							else
							{
								
								echo "You have no Virtual Node Group . Lets create one. ".'<a class="add-links" href="'.ROOTURL.'/virtual-nodegroups" " id="create_new_virtual_node_group" >Add New Property Set</a>';
							}
						    break;
							
							
			case "testbeds"	:
							$html='<h4>TestBeds</h4><table cellspacing="0" id="expandable-table" class="table-list"><tr><th width="50%" style="text-align:left;padding-left:10px;">Name</th><th width="20%" style="text-align:left;">Organization</th><th width="15%">Node Count</th><th width="5%">Link</th><th></th></tr>';
							$TestBeds=FollowTestBeds();
							if(!empty($TestBeds))
							{
								foreach ($TestBeds as $TestBed)
								{
									$TestBed_info=$TestBed;
														
									$html.="<td style='text-align:left;padding-left:10px;'>".$TestBed_info['name'].'</td><td>'.$TestBed_info['organization'].'</td><td >'.$TestBed_info['node_count'].'</td><td ><a href="'.$TestBed_info['server_url'].'" target="_new"> Click </a></td><td><div class="arrow"></div></td></tr>';
									$html.="<td colspan='5'>".$TestBed_info['description']."</td>";
								}
								$html.='<tr><td class="last_row" colspan="6" style="height: 16px;"></td></tr></table> ';
							}
							
							echo $html;
							break;
			case 'properties': 	$propertyset=FollowPropertySets($_POST['pid']);
								$propertyset_s="";
								
								foreach($propertyset as $property)
								{
									$propertyset_s.='<li><a href="'.ROOTURL."/experiments/".$_POST['pid'].'/property-sets/'.$property['id'].'" class="item-edit" >'.$property['name'].'</a></li>';
								}
			
								$html='<ul id="drop-down">
									  <li><a href="#">PropertySet</a>
										<ul id="property-set-tab">
										'.$propertyset_s.'
										  <li><a href="'.ROOTURL."/experiments/".$_POST['pid']."/property-sets".'" class="drop-down-bottom" id="create_new_property_set">Add PropertySet</a></li>
										 
										</ul>
									  </li>
									  <li><a href="#">Virtual Node Group</a>
										<ul id="virtual-node-group-tab">
										  <li><a href="'.ROOTURL."/experiments/".$_POST['pid']."/virtual-nodegroups".'" class="drop-down-bottom" id="create_new_virtual_node_group">Add Virtual Node Group</a></li>
										  
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
									</ul>';
									echo $html;
			
							   break;							
								
		}
	}
	elseif(isset($_POST['Delete']) && !empty($_POST['Delete']))
	{
		echo deleteResource(trim($_POST['Delete']));
	}
	elseif(isset($_POST['Update']) && !empty($_POST['Update']))
	{
		$item=trim($_POST['Update']);
		$uriPath=parse_url($item,PHP_URL_PATH);
		$conditions=explode('/',$uriPath);
		
		if(count($conditions)==2)//add
		{
			switch ($conditions[1])
			{
				case 'projects':echo CreateProjectForm('');break;
				case 'experiments':echo CreateExperimentForm(''); break;
				//case 'property-sets':echo CreatePropertySetForm(''); break;
				case 'virtual-nodegroups':echo CreateVNGForm('');break;
			}
		}
		elseif (count($conditions)==3)//update
		{
			
			switch ($conditions[1])
			{
				case 'projects':echo CreateProjectForm($item);break;
				case 'experiments':echo CreateExperimentForm($item); break;
				//case 'property-sets':echo CreatePropertySetForm($item,''); break;
				case 'virtual-nodegroups':echo CreateVNGForm($item);break;
			}
		}
		elseif(count($conditions)==4)
		{
			
			switch ($conditions[3])
			{
				case 'property-sets':echo CreatePropertySetForm('',$_POST['pid']); break;
			}
		}
		elseif(count($conditions)==5)
		{
			switch ($conditions[3])
			{
				case 'property-sets':echo CreatePropertySetForm($_POST['Update'],$_POST['pid']); break;
			}
		}
		
		
	}
	elseif (isset($_POST['Submit']) && !empty($_POST['Submit']))
	{
		if(isset($_POST['form-type']))
		{
			switch($_POST['form-type'])
			{
				case 'project':
							    $params=$_POST;
								unset($params['Submit']);
								unset($params['form-type'])	;								
								$resp=RESTUrl(ROOTURL.'/projects/','POST',json_encode($params));
								echo getResponseCode($resp);
								break;
				case 'projectUpdate':
								$uri=trim($_POST['uri']);
								$params=$_POST;
								unset($params['Submit']);
								unset($params['form-type']);
								unset($params['uri']);
								$resp=RESTUrl($uri,'PUT',json_encode($params));
								echo getResponseCode($resp);
								break;
				case 'experiment':	
								$params=$_POST;				
								unset($params['Submit']); 
								unset($params['form-type']);
								$resp=RESTUrl(ROOTURL.'/experiments/','POST',json_encode($params));
								echo getResponseCode($resp);
								break;
				case 'experimentUpdate':
								$uri=trim($_POST['uri']);
								$params=$_POST;
								unset($params['Submit']);
								unset($params['uri']);
								unset($params['form-type']);
								$resp=RESTUrl($uri,'PUT',json_encode($params));
								echo getResponseCode($resp);							
								break;
				case 'property-set':
								$params=$_POST;	
								$exp=$params['experiments'];
								unset($params['experiments']);
								unset($params['Submit']); 
								unset($params['form-type']);
								$resp=RESTUrl(ROOTURL.'/experiments/'.$exp.'/property-sets/','POST',json_encode($params,JSON_NUMERIC_CHECK));
								echo getResponseCode($resp);
								break;
				case 'property-setUpdate':
								$uri=trim($_POST['uri']);
								$params=$_POST;
								$exp=$params['experiments'];
								$id=$params['uri'];
								unset($params['experiments']);
								unset($params['uri']);
								unset($params['Submit']);
								unset($params['form-type']);
								unset($params['uri']);								
								$resp=RESTUrl(ROOTURL.'/experiments/'.$exp.'/property-sets/'.$id,'POST',json_encode($params,JSON_NUMERIC_CHECK));
								echo getResponseCode($resp);
								break;									
				case "VNG":		
								
								$params=$_POST;
								unset($params['Submit']);
								unset($params['form-type']);
								$nodes=explode(',',$params['virtual_nodes']);
								unset($nodes[count($nodes)-1]);
								$params['virtual_nodes']=$nodes;
								//echo json_encode($params);								
								$resp=RESTUrl(ROOTURL.'/virtual-nodegroups/','POST',json_encode($params));
								echo getResponseCode($resp);
								break;		
			}
			
		}
		
		
	}
	//submit ends here
}	
?>