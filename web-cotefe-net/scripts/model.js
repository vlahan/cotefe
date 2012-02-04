

/**************************************************************************************
 * 
 * UI Model class and packages
 * 
 * ************************************************************************************
 */


//project
var resProject=function(uri,name,desc,experiments,jobs){
	this.uri=uri;
	this.name=name;
	this.desc=desc;	
	this.experiments=experiments
	this.jobs=jobs;
}

//experiment
var resExperiment=function(uri,name,desc,projectname,testbeds,images,propertySets,virtualTasks,vgns,vn
	,jobs,traces){
	this.uri=uri;
	this.name=name;
	this.desc=desc;
	this.project=projectname;
	this.testbeds=testbeds;
	this.images=images;
	this.propertySets=propertySets;
	this.virtualTasks=virtualTasks;
	this.vgns=vgns;
	this.vn=vn;
	this.jobs=jobs;
	this.traces=traces;
}

//property set
var resPropertySet=function(uri,name,desc,experiment,platform,radios,interfaces,sensors,actuators
	,mobility,nodes){	
	this.uri=uri;
	this.name=name;
	this.desc=desc;
	this.experiment=experiment;
	this.platform=platform;
	this.radios=radios;
	this.interfaces=interfaces;
	this.sensors=sensors;
	this.actuators=actuators;
	this.mobility=mobility;
	this.nodes=nodes;	
}

//virtual node group
var resVNG=function(uri,name,virtualNodes){
	this.uri=uri;
	this.name=name;
	this.virtualNodes=virtualNodes;
}

//virtual node
var resVN=function(uri,name,propertySet){
	this.uri=uri;
	this.name=name;
	this.propertySet=propertySet;
}

//virtual task
var resVT=function(uri,name,desc,eta,method,headers,payload,target){
	this.uri=uri;
	this.name=name;
	this.desc=desc;
	this.eta=eta;
	this.method=method;
	this.headers=headers;
	this.payload=payload;
	this.target=target;
}

//one platform
var resPlatform=function(uri,name,desc){
	this.uri=uri;
	this.name=name;
	this.desc=desc;
}

//one test bed
var resTestBed=function(uri,name,desc,org,serverUrl){
	this.uri=uri;
	this.name=name;
	this.desc=desc;
	this.org=org;
	this.serverUrl=serverUrl;
}

//radio
var resRadio= function(uri,name){
	this.uri=uri;
	this.name=name;
}

//sensor
var resSensor=function(uri,name,desc,values,units){
	this.uri=uri;
	this.name=name;
	this.desc=desc;
	this.values=values;
	this.units=units;
}

//actuator
var resActuator=function(uri,name,desc,values,units){
	this.uri=uri;
	this.name=name;
	this.desc=desc;
	this.values=values;
	this.units=units;
}

//mobility
var resMobility=function(uri,name,desc){
	this.uri=uri;
	this.name=name;
	this.desc=desc;
}

//user 
var resUser=function(uri,name,openid,email,org,projects,exp,jobs)
{
	this.uri=uri;
	this.name=name;
	this.openid=openid;
	this.email=email;
	this.org=org;
	this.projects=projects;
	this.exp=exp;
	this.jobs=jobs;
}



/*
 * test
 */
