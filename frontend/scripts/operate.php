<?php
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
							$header[0]['attribute']='width="40%" style="text-align:left;padding-left:10px;"';
							$header[1]['text']='No. Of Experiment';
							$header[1]['attribute']='style="text-align:center;"';
							$header[2]['text']='Edit';
							$header[2]['attribute']='width="5%"';
							$header[3]['text']='Delete';
							$header[3]['attribute']='width="7%"';
							
							$records=array();
							$projects=FollowProject();
							if(!empty($projects))
							{
								$i=0;
								foreach ($projects as $project)
								{
									$project_info=json_decode(getUrl($project['uri']),TRUE);
									$exp_count=count($project_info["experiments"]);
									$records[$i][0]['text']=$project_info['name'];
									$records[$i][0]['attribute']='style="padding-left:10px;"';
									$records[$i][1]['text']=$exp_count;
									$records[$i][1]['attribute']='style="text-align:center;"';
									$records[$i][2]['text']='<a class="edit" href="'.$project_info['uri'].'" ><img src="images/edit.png" /></a>';
									$records[$i][2]['attribute']='style="padding-left:10px;"';
									$records[$i][3]['text']='<a class="deleteProject" href="'.$project_info['uri'].'"><img src="images/close.png" /></a>';
									$records[$i][3]['attribute']='style="padding-left:15px;"';
									
									
									$i++;
								}
								$records[$i][0]['text']='<a class="add-links" href="'.ROOTURL.'/projects" " id="create_new_project" >Add New Project +</a>';
								$records[$i][0]['attribute']='style="padding-left:10px;"';
								$records[$i][1]['text']=$records[$i][2]['text']=$records[$i][3]['text']='';
								$obj=new Createtable($title,$header,$records);
								echo $obj->render();
							}
							else
							{
								echo "You have no projects . Lets create One.";
							}
						    break;
							
							
							
			case "experiment":
							$html='<h4>Experiments List</h4><table cellspacing="0"><tr><th width="20%">Name</th><th width="20%">Project</th><th>VN</th><th>Description</th><th width="5%">Edit</th><th width="7%">Delete</th></tr>';
							$experiments=FollowExperiment();
							if(!empty($experiments))
							{
								foreach ($experiments as $experiment)
								{
									$experiment_info=json_decode(getUrl($experiment['uri']),TRUE);
									$project_info=json_decode(getUrl($experiment_info['project']),TRUE);				
									$html.="<td>".$experiment_info['name'].'</td><td>'.$project_info['name'].'</td><td>'.$experiment_info['node_count'].'</td><td class="description"  >'.shortenString($experiment_info['description'],50).'</td><td class="center_text" ><a class="edit" href="'.$experiment_info['uri'].'"><img src="images/edit.png" /></a></td><td class="center_text" ><a class="deleteProject" href="'.$experiment_info['uri'].'"><img src="images/close.png" /></a></td></tr>';
								
								}
								$html.='<tr><td class="last_row" colspan="6" style="height: 16px;"></td></tr></table> ';
							}
							echo $html;
						    break;
			case "property-sets":
							$html='<h4>Property Set List</h4><table cellspacing="0"><tr><th width="20%">Name</th><th width="20%">Experiment</th><th>Platform</th><th>VN</th><th>Description</th><th width="5%">Edit</th><th width="7%">Delete</th></tr>';
							$property_sets=FollowPropertySets();
							if(!empty($property_sets))
							{
								foreach ($property_sets as $property_set)
								{
									$property_set_info=json_decode(getUrl($property_set['uri']),TRUE);
									$experiment_info=json_decode(getUrl($property_set_info['experiment']),TRUE);
									$platform_info=json_decode(getUrl($property_set_info['platform']),TRUE);						
									$html.="<td>".$property_set_info['name'].'</td><td>'.$experiment_info['name'].'</td><td>'.$platform_info['name'].'</td><td>'.$property_set_info['node_count'].'</td><td class="description"  >'.shortenString($property_set_info['description'],50).'</td><td class="center_text" ><a class="edit" href="'.$property_set_info['uri'].'"><img src="images/view.png" /></a></td><td class="center_text" ><a class="deleteProject" href="'.$property_set_info['uri'].'"><img src="images/close.png" /></a></td></tr>';
								}
								$html.='<tr><td class="last_row" colspan="7" style="height: 16px;"></td></tr></table> ';
							}
							echo $html;
							break;
			case "virtual-nodegroups":
							$html='<h4>Virtual Node Groups</h4><table cellspacing="0"><tr><th width="20%">Name</th><th width="20%">Experiment</th><th width="10%">VN</th><th>Description</th><th width="5%">Edit</th><th width="7%">Delete</th></tr>';
							$VirtualNodesGroups=FollowVirtualNodeGroup();
							if(!empty($VirtualNodesGroups))
							{
								foreach ($VirtualNodesGroups as $VirtualNodesGroup)
								{
									$VirtualNodesGroup_info=json_decode(getUrl($VirtualNodesGroup['uri']),TRUE);
									$experiment_info=json_decode(getUrl($VirtualNodesGroup_info['experiment']),TRUE);
															
									$html.="<td>".$VirtualNodesGroup_info['name'].'</td><td>'.$experiment_info['name'].'</td><td>'.$VirtualNodesGroup_info['node_count'].'</td><td class="description"  >'.shortenString($VirtualNodesGroup_info['description'],50).'</td><td class="center_text" ><a class="edit" href="'.$VirtualNodesGroup_info['uri'].'"><img src="images/edit.png" /></a></td><td class="center_text" ><a class="deleteProject" href="'.$VirtualNodesGroup_info['uri'].'"><img src="images/close.png" /></a></td></tr>';
								}
								$html.='<tr><td class="last_row" colspan="6" style="height: 16px;"></td></tr></table> ';
							}
							echo $html;
							break;
			case "testbeds"	:
							$html='<h4>TestBeds</h4><table cellspacing="0" id="expandable-table"><tr><th width="55%">Name</th><th width="20%">Organization</th><th width="15%">Node Count</th><th width="5%">Link</th><th></th></tr>';
							$TestBeds=FollowTestBeds();
							if(!empty($TestBeds))
							{
								foreach ($TestBeds as $TestBed)
								{
									$TestBed_info=json_decode(getUrl($TestBed['uri']),TRUE);
														
									$html.="<td>".$TestBed_info['name'].'</td><td>'.$TestBed_info['organization'].'</td><td >'.$TestBed_info['node_count'].'</td><td ><a href="'.$TestBed_info['url'].'" target="_new"> Click </a></td><td><div class="arrow"></div></td></tr>';
									$html.="<td colspan='5'>".$TestBed_info['description']."</td>";
								}
								$html.='<tr><td class="last_row" colspan="6" style="height: 16px;"></td></tr></table> ';
							}
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
				case 'property-sets':echo CreatePropertySetForm(''); break;
				case 'virtual-nodegroups':echo CreateVNGForm('');break;
			}
		}
		elseif (count($conditions)==3)//update
		{
			
			switch ($conditions[1])
			{
				case 'projects':echo CreateProjectForm($item);break;
				case 'experiments':echo CreateExperimentForm($item); break;
				case 'property-sets':echo CreatePropertySetForm($item); break;
				case 'virtual-nodegroups':echo CreateVNGForm($item);break;
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
								unset($params['Submit']); 
								unset($params['form-type']);
								$resp=RESTUrl(ROOTURL.'/property-sets/','POST',json_encode($params,JSON_NUMERIC_CHECK));
								echo getResponseCode($resp);
								break;
				case 'property-setUpdate':
								$uri=trim($_POST['uri']);
								$params=$_POST;
								unset($params['Submit']);
								unset($params['form-type']);
								unset($params['uri']);								
								$resp=RESTUrl($uri,'PUT',json_encode($params));
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