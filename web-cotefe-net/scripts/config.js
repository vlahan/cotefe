/*
 * configuration file
 */
 var cotefe = {
        mainUri             : "http://localhost:8080",
        apiUri              : "https://api.cotefe.net",
        version             : 1.0,
        projects            : {uri:"projects/",         session:"_cotefeProject"},
        experiments         : {uri:"experiments/",      session:"_cotefeExperiments"},
        jobs                : {uri:"jobs/",             session:"_cotefeJobs"},
        platforms           : {uri:"platforms/",        session:"_cotefePlatforms"},
        testbeds            : {uri:"testbeds/",         session:"_cotefeTestbeds"},
        user                : {uri:"me",                session:"_cotefeUser"},
        oauth               : "https://api.cotefe.net/oauth2/auth?client_id=4e6b4b547b344429a52b4ce0d020f941",       
        redirect            : "http://localhost:8080/htmls/getdata.html&response_type=token",
        dashboard           : "/dashboard",        
        comment             : "JS configuration ",
        link                : function(path){return this.apiUri+"/"+path+"";},
        link2               : function(path,token){return (path+"?access_token="+token);},
        linkTok             : function(path,token){return (this.link(path)+"?access_token="+token);},
        log                 : function(value){console.log(value);},
        signOut             : function(){cotefe.session.clearAll();window.location.href=this.mainUri;},
        debug               : false,
    };

/*
 * a j a x configuration and operation
 */
cotefe.ajax                         = {};
cotefe.ajax.newRequest              = function()
{
    var factories = [function() { return new ActiveXObject("Msxml2.XMLHTTP"); },function() { return new XMLHttpRequest(); },function() { return new ActiveXObject("Microsoft.XMLHTTP"); }];
        for(var i = 0; i < factories.length; i++) {
            try {
                    var request = factories[i]();
                    if (request != null)  return request;
                }
            catch(e) { continue;}
        }
};
cotefe.ajax.ajaxCounter             = {
                                        counter:0,
                                        up:function(){this.counter++;},down:function(){this.counter--;},
                                        getCount:function(){return this.counter;}
                                    };
cotefe.ajax.getAjaxResponse         = function(params)
{
    return params.responseText;
};
cotefe.ajax.getAjaxStatus           = function(params)
{
    return params.status;
};
cotefe.ajax.binder                  = function(request,data){
                                          this.request  =request;
                                          this.status   =cotefe.ajax.getAjaxStatus(data);
                                          this.data     =cotefe.ajax.getAjaxResponse(data); 
                                      };
cotefe.ajax.ajax_request            = function(params){
        
        params.method = ( params.method ? params.method : 'GET');
        params.payload= ( params.payload ? params.payload: null);
        var request = new cotefe.ajax.newRequest();
        cotefe.ajax.ajaxCounter.up(); //increase coming connection number
        request.onreadystatechange = function(){
            if(request.readyState == 4){
                cotefe.ajax.ajaxCounter.down();//decrease connection number
                
                if(request.status == 200){
                    params.onComplete(new cotefe.ajax.binder(params,request))
                }else
                {
                    params.onComplete(new cotefe.ajax.binder(params,request))
                }
                
            }
            else
            {
                
            }
        }
        request.open(params.method , params.uri);
        request.send(params.payload);
};
cotefe.ajax.onAllAjaxDone           = function()
                                 {
                                     if(cotefe.ajax.ajaxCounter.getCount()===0)
                                     {
                                         window.location.href=cotefe.dashboard;
                                     }
                                 }


/*
 * session creation,handler,destroyer, modifier
 */
cotefe.session                      = {};
cotefe.session.init                 = function(){
    
    if(sessionStorage.setItem(cotefe.user.session,"") === null)
    {
        return false;
    }
    else
    {
        sessionStorage.setItem(cotefe.projects.session,"");
        sessionStorage.setItem(cotefe.experiments.session,"");
        sessionStorage.setItem(cotefe.jobs.session,"");
        sessionStorage.setItem(cotefe.platforms.session,"");
        sessionStorage.setItem(cotefe.testbeds.session,"");
        return true;
    }   
};
cotefe.session.write                = function(key,value)
{
    if(sessionStorage.setItem(key,value))
        {
            return true;
        }
        else
        {
            return false;
        }
}
cotefe.session.clearAll             = function(){
                                    sessionStorage.removeItem(cotefe.user.session);
                                    sessionStorage.removeItem(cotefe.projects.session);
                                    sessionStorage.removeItem(cotefe.experiments.session);
                                    sessionStorage.removeItem(cotefe.jobs.session);
                                    sessionStorage.removeItem(cotefe.testbeds.session);
                                    sessionStorage.removeItem(cotefe.platforms.session);
                              };
cotefe.session.FindItemByUri        = function(type,uri)
{
    var obj=JSON.parse(sessionStorage.getItem(type));
    for(i=0;i<obj.length;i++)
    {
        singleObj=JSON.parse(obj[i]);
        if(singleObj.uri===uri)
        {
            return singleObj;
        }
     
    }
    return null;
};
cotefe.session.writeResource        = function(params)
{
    //TODO: write information or update in session
};
cotefe.session.getValueFromKey      = function(params){return (sessionStorage.getItem(params)?JSON.parse(sessionStorage.getItem(params)):null);};
/*
 * default alerts
 */
cotefe.alerts                       = {};
cotefe.alerts.success               = function(params){
    params.custom = ( (params.custom===false || params.custom===undefined) ? false : params.custom);
    if(params.custom===false)
    {
        alert("operation was a big success");
    }
    else
    {
        alert("Custom event triggered");
    }
}
cotefe.alerts.warning               = function(params){
    params.custom = ( (params.custom===false || params.custom===undefined) ? false : params.custom);
    if(params.custom===false)
    {
        alert("operation has a warning");
    }
    else
    {
        alert("Custom event triggered");
    }
}
cotefe.alerts.fail                  = function(params){
    params.custom = ( (params.custom===false || params.custom===undefined) ? false : params.custom);
    if(params.custom===false)
    {
        alert("operation failed");
    }
    else
    {
        alert("Custom event triggered");
    }
}

/*
 * method to generate custom resource to does the ajax request 
 * it triggers onComplete event when done
 */
cotefe.method                       = {};
cotefe.method.get                   = function(params){
    if(params.uri)
    {
        obj={method:"GET",uri:cotefe.link2(params.uri,params.token),onComplete:function(result){params.onComplete(result);},params:params}
        cotefe.ajax.ajax_request(obj);
    }
    else if(params.type)
    {
        obj={method:"GET",uri:cotefe.linkTok(params.type,params.token),onComplete:function(result){params.onComplete(result);},params:params}
        cotefe.ajax.ajax_request(obj);
    }
};
cotefe.method.post                  = function(params){
   obj={method:"POST",uri:cotefe.linkTok(params.type,params.token),payload:params.payload,onComplete:function(result){params.onComplete(result);},params:params}
   cotefe.ajax.ajax_request(obj);
    
}
cotefe.method.put                   = function(params){
    if(params.uri)
    {
        cotefe.log(params);
    	obj={method:"PUT",uri:cotefe.link2(params.uri,params.token),payload:params.payload,onComplete:function(result){params.onComplete(result);},params:params}
        cotefe.ajax.ajax_request(obj);
    }
}
cotefe.method.del                   = function(params){
    if(params.uri)
    {
        cotefe.log(params);
    	obj={method:"DELETE",uri:cotefe.link2(params.uri,params.token),onComplete:function(result){params.onComplete(result);},params:params}
        cotefe.ajax.ajax_request(obj);
    }
}
//cotefe.method.get({type:(cotefe.projects.uri),token:"1f6305daff1e499bb16ad6ec12c40dd7",onComplete:function(data){cotefe.log(data)}});
//string="{\"name\":\"testjson\",\"description\":\"desc\"}";
//cotefe.method.post({type:(cotefe.projects.uri),token:"1f6305daff1e499bb16ad6ec12c40dd7",payload:string,onComplete:function(data){cotefe.log(data)}});


/********************** Application *************************************/
/*
 * on first load get all data and save to session
 * 1. save user info with token
 * 3. get user each project and save in session
 * 2. get user projects list
 * 5. repeat 2 and 3 for experiment and job
 * 6. get platforms and test-beds
 * 7. once done send user to his dash-board
 */
cotefe.application                  = {};
cotefe.application.getUser          = function(token){
    
    cotefe.method.get({token:token,type:cotefe.user.uri,onComplete:function(data){cotefe.application.onUserSuccess(data);}});
};
cotefe.application.onUserSuccess    = function(data){
    //cotefe.log(data);
    if(data.status===200)
    {
        //cotefe.session.init();
       if(data.request.params.type)
       {
           switch(data.request.params.type)
           {
               case cotefe.user.uri: obj=JSON.parse(data.data);
               						 obj.session=data.request.params.token;
               						 
            	   					 cotefe.session.write(cotefe.user.session,JSON.stringify(obj));
                                     cotefe.application.getResourceOfType({token:data.request.params.token,type:cotefe.projects.uri});
                                     //cotefe.application.getResourceOfType({token:data.request.params.token,type:cotefe.experiments.uri});
                                     //cotefe.application.getResourceOfType({token:data.request.params.token,type:cotefe.jobs.uri});
                                     cotefe.application.getResourceOfType({token:data.request.params.token,type:cotefe.platforms.uri});
                                     cotefe.application.getResourceOfType({token:data.request.params.token,type:cotefe.testbeds.uri});
                                     break;
           }
       }
    }
};

cotefe.application.getResourceOfType   		= function(params)
{
    cotefe.method.get({token:params.token,type:params.type,onComplete:function(data){cotefe.application.onGetResourceSuccess(data);}});
};
cotefe.application.onGetResourceSuccess		= function(data)
{
    //cotefe.log(data);
    if(data.status===200)
    {
        switch(data.request.params.type)
        {
            case cotefe.projects.uri    :  
            								data.session=cotefe.projects.session;
                                            cotefe.application.operations.digLinks(data);
                                            cotefe.ajax.onAllAjaxDone();break;
            case cotefe.experiments.uri : cotefe.session.write(cotefe.experiments.session,data.data);cotefe.ajax.onAllAjaxDone();break;
            case cotefe.jobs.uri        : cotefe.session.write(cotefe.jobs.session,data.data);cotefe.ajax.onAllAjaxDone();break;
            case cotefe.platforms.uri   : 	//data.session=cotefe.platforms.session;
									        //cotefe.application.operations.digLinks(data);
									        //cotefe.ajax.onAllAjaxDone();break;
            								cotefe.session.write(cotefe.platforms.session,data.data);cotefe.ajax.onAllAjaxDone();break;
            case cotefe.testbeds.uri    : cotefe.session.write(cotefe.testbeds.session,data.data);cotefe.ajax.onAllAjaxDone();break;
        }
    }
}

cotefe.application.createUpdateResource=function(params)
{
	token=(JSON.parse(sessionStorage.getItem(cotefe.user.session))).session;
	
	switch(params.head.method)
	{
		case "POST"		:cotefe.method.post({type:params.head.type,token:token,payload:params.data,onComplete:function(data){cotefe.log(data)}});break;
		case "PUT"		:cotefe.method.put({uri:params.head.type,token:token,payload:params.data,onComplete:function(data){cotefe.log(data)}});break;
		case "DELETE"	:cotefe.method.del({uri:params.head.uri,token:token,onComplete:function(data){cotefe.log(data)}});break;
	}
}

cotefe.application.operations				= {};
cotefe.application.operations.dumbList  	= []; //dummy list
cotefe.application.operations.addToDumbList = function(params)
{
    cotefe.application.operations.dumbList.push(params.data);
}

cotefe.application.operations.digLinks   	= function(params)
{
       obj=JSON.parse(params.data);
       //cotefe.log(params);
       for(i=0;i<obj.length;i++)
           {
    	   		objv={method:"GET",
    	   			  uri:cotefe.link2(obj[i].uri,
    	   			  params.request.params.token),
    	   			  onComplete:function(result)
    	   			  	{
    	   				  cotefe.application.operations.addToDumbList(result);
                          cotefe.session.write(params.session,JSON.stringify(cotefe.application.operations.dumbList));
                          cotefe.ajax.onAllAjaxDone();
    	   			  	},
    	   			 params:params}
    	   		cotefe.ajax.ajax_request(objv);
           }
};










