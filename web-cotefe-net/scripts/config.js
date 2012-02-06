/*
 * configuration file
 */
 var cotefe = {
        mainUri             : "http://localhost:8080",
        apiUri              : "https://api.cotefe.net",
        version             : 1.0,
        projects            : "projects/",
        experiments         : "experiments/",
        jobs                : "jobs/",
        platforms           : "platforms/",
        testbeds            : "testbeds/",
        oauth               : "https://api.cotefe.net/oauth2/auth?client_id=4e6b4b547b344429a52b4ce0d020f941",
        me                  : "me",
        redirect            : "http://localhost:8080/htmls/getdata.html&response_type=token",
        dashboard           : "/dashboard",        
        comment             : "JS configuration ",
        localUser           : "_cotefeUser",
        localUserProject    : "_cotefeProject",
        localUserExperiment : "_cotefeExperiments",
        localUserJobs       : "_cotefeJobs",
        localUserPlatform   : "_cotefePlatforms",
        localUserTestBeds   : "_cotefeTestBeds",        
        link                : function(path){return this.apiUri+"/"+path+"";},
        link2               : function(path,token){return (path+"?access_token="+token);},
        linkTok             : function(path,token){return (this.link(path)+"?access_token="+token);},
        log                 : function(value){console.log(value);},
        token               : "",
        signOut             : function(){cotefe.session.clearAll();window.location.href=this.mainUri;},
        debug               : false,
    };


 
/*
 * ajax events and response handlers
 */

cotefe.newRequest               = function()
{
    var factories = [function() { return new ActiveXObject("Msxml2.XMLHTTP"); },function() { return new XMLHttpRequest(); },function() { return new ActiveXObject("Microsoft.XMLHTTP"); }];
        for(var i = 0; i < factories.length; i++) {
            try {
                    var request = factories[i]();
                    if (request != null)  return request;
                }
            catch(e) { continue;}
        }
}
cotefe.ajaxCounter              = {counter:0,up:function(){this.counter++;},down:function(){this.counter--;},getCount:function(){return this.counter;}}
cotefe.ajax_request             = function(params){
        
        params.method = ( params.method ? params.method : 'GET');
        
        params.payload= ( params.payload ? params.payload: null);
        var request = new cotefe.newRequest();
        cotefe.ajaxCounter.up(); //increase coming connection number
        request.onreadystatechange = function(){
            if(request.readyState == 4){
                cotefe.ajaxCounter.down();//decrease connection number
                if(request.status == 200){
                    params.onComplete(request)
                }else
                {
                    params.onComplete(request)
                }
                
            }
            else
            {
                
            }
        }
        request.open(params.method , params.url);
        request.send(params.payload);
    }
cotefe.getAjaxResponse          = function(params)
{
    return params.responseText;
}
cotefe.getAjaxStatus            = function(params)
{
    return params.status;
}

/*
 * session storage handler
 */
cotefe.session                  = {};
cotefe.session.create           = function(){
    
    if(sessionStorage.setItem(cotefe.localUser,"") === null)
    {
        return false;
    }
    else
    {
        sessionStorage.setItem(cotefe.localUserProject,"");
        sessionStorage.setItem(cotefe.localUserExperiment,"");
        sessionStorage.setItem(cotefe.localUserJobs,"");
        sessionStorage.setItem(cotefe.localUserPlatform,"");
        sessionStorage.setItem(cotefe.localUserTestBeds,"");
        return true;
    }
}
cotefe.session.write            = function(key,value)
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
cotefe.session.clearAll         = function(){
                                    sessionStorage.removeItem(cotefe.localUser);
                                    sessionStorage.removeItem(cotefe.localUserProject);
                                    sessionStorage.removeItem(cotefe.localUserExperiment);
                                    sessionStorage.removeItem(cotefe.localUserJobs);
                                    sessionStorage.removeItem(cotefe.localUserPlatform);
                                    sessionStorage.removeItem(cotefe.localUserTestBeds);
                                  },
cotefe.session.FindItemByUri    = function(type,uri){
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
cotefe.session.writeResource	= function(data)
									{
										
										
										if((data.url===cotefe.projects || 
											data.url===cotefe.experiments ||
											data.url===cotefe.jobs
											) && (data.method==="POST"))
										{											
											/*
											 * post new resource and update session
											 */
											var params=cotefe.method.postResource((cotefe.application.user).session,data.url,data.payload,cotefe.application.updateSuccess);
											
											cotefe.ajax_request(params);
										}
										else
										{
											cotefe.log("here !!");
										}
										
										
									}
                                    /*
 * get,post,put,delete
 */
cotefe.method                   = {};
cotefe.method.binder            = function(data){
                                      this.status=cotefe.getAjaxStatus(data);
                                      this.data=cotefe.getAjaxResponse(data); 
                                      };
cotefe.method.getResource       = function(token,type,success){
                        return {method:"GET",url:(cotefe.linkTok(type,token)),onComplete:function(result){success(token,type,new cotefe.method.binder(result))}};                                     
                  };
cotefe.method.postResource      = function(token,type,payloads,success){
                        return {method:"POST",url:(cotefe.linkTok(type,token)),payload:payloads,onComplete:function(result){success(token,type,new cotefe.method.binder(result))}};                                     
                  };
cotefe.method.putResource       = function(token,type,payloads,success){
                        return {method:"PUT",url:(cotefe.linkTok(type,token)),payload:payloads,onComplete:function(result){success(token,type,new cotefe.method.binder(result))}};                                     
                  };
cotefe.method.deleteResource    = function(token,type,success){
                        return {method:"DELETE",url:(cotefe.linkTok(type,token)),onComplete:function(result){success(token,type,new cotefe.method.binder(result))}};                                     
                  };

/*
 * on first load get all data and save to session
 * 1. save user info with token
 * 2. get user projects list
 * 3. get user each project and save in session
 * 5. repeat 2 and 3 for experiment and job
 * 6. get platforms and test-beds
 * 7. once done send user to his dash-board
 */

cotefe.application              = {};
/*
 * 1 getting user me
 */
cotefe.application.getUserInfo  = function(token,type,success)
                                {
                                        return cotefe.method.getResource(token,type,success);
                                };
/*
 * 2 set user in storage and call rest of resources
 */
cotefe.application.onMeDone     = function(token,type,data)
                            {                               
                                
                                if(data.status === 200)
                                {
                                    var obj=JSON.parse(data.data);
                                    obj.session=access_token; //add session attribute
                                    var jsonA=JSON.stringify(obj); 
                                    if(cotefe.session.create()) //create empty session variables
                                    {
                                        cotefe.session.write(cotefe.localUser,jsonA);
                                        cotefe.log("User Written");
                                        //get projects
                                        cotefe.ajax_request(cotefe.application.getUserInfo(token,cotefe.projects,cotefe.application.onMeRestDone));
                                        //get experiments
                                        //cotefe.ajax_request(cotefe.application.getUserInfo(token,cotefe.experiments,cotefe.application.onMeRestDone));
                                        //get jobs
                                        //cotefe.ajax_request(cotefe.application.getUserInfo(token,cotefe.jobs,cotefe.application.onMeRestDone));
                                        //get platforms
                                        cotefe.ajax_request(cotefe.application.getUserInfo(token,cotefe.platforms,cotefe.application.onMeRestDone));   
                                        //get test-beds
                                        cotefe.ajax_request(cotefe.application.getUserInfo(token,cotefe.testbeds,cotefe.application.onMeRestDone));                                                                         
                                    }
                                    else
                                    {
                                        console.log("Session Failed");
                                    }
                                }
                                else
                                {
                                    alert("There was some problem by Login.Please try again later!!"+cotefe.getAjaxStatus(data));
                                    //document.location.href=cotefe.mainUri;
                                }                                
                            };           
/*
 * rest of resource saved in session 
 * checks connection left, once connection are 0 tell user to change page : dash-board
 */
cotefe.application.onMeRestDone = function(token,type,data)
                                {
                                    
                                    switch(type)
                                    {
                                        case cotefe.platforms   :cotefe.session.write(cotefe.localUserPlatform,data.data);cotefe.application.onAllDone();break; 
                                        case cotefe.projects    :   cotefe.application.list({token:token,json:data.data,sessionId:cotefe.localUserProject});
                                                                    break;
                                        case cotefe.experiments :console.log(data.data);break;
                                        case cotefe.jobs        :console.log(data.data);break;
                                        case cotefe.testbeds    :cotefe.session.write(cotefe.localUserTestBeds,data.data);cotefe.application.onAllDone();break;
                                    }
                                    
                                }               

/*
 * check number of connection and redirect
 */
cotefe.application.onAllDone    = function()
                                 {
                                     if(cotefe.ajaxCounter.getCount()===0)
                                     {
                                         window.location.href=cotefe.dashboard;
                                     }
                                 }

/*
 * get user info as object
 */
cotefe.application.user         = JSON.parse(sessionStorage.getItem(cotefe.localUser));

/*
 * j-son to object array
 * 
 */
cotefe.application.dumbObj      = [];
//creates list of inner object and saves in given session Variable
cotefe.application.list         = function(params)
                                    {
                                      cotefe.application.dumbObj=[];
                                      objLi=JSON.parse(params.json);
                                      if(objLi === null || objLi.length === 0)
                                      {
                                          return null;
                                      }
                                      else
                                      {
                                          
                                          for(i=0;i<objLi.length;i++)
                                          {
                                              
                                              cotefe.ajax_request({method:"GET",url:(objLi[i].uri+"?access_token="+params.token),onComplete:function(data){
                                                                                                                                            cotefe.application.addToDumbArray(data);
                                                                                                                                            cotefe.session.write(params.sessionId,JSON.stringify(cotefe.application.dumbObj));
                                                                                                                                            cotefe.application.onAllDone();

                                                                                                                                            }});
                                          }
                                      }  
                                      
                                    };
cotefe.application.addToDumbArray = function(val)
{
    data=cotefe.getAjaxResponse(val);
    cotefe.application.dumbObj.push(data);
}

/*
 * add to server and to current session
 */
cotefe.application.update		= function(params)
								 {
									cotefe.log(params);
									cotefe.session.writeResource(params);
								 }

cotefe.application.updateSuccess     = function(token,type,data)
{
	cotefe.log(data);
	cotefe.log("Alarm");
}
