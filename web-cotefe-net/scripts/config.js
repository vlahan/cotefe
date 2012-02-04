/*
 * configuration file
 */
 var cotefe = {
        mainUri             : "http://localhost:8080",
        apiUri              : "http://api.cotefe.net",
        version             : 1.0,
        projects            : "projects/",
        experiments         : "experiments/",
        jobs                : "jobs/",
        platforms           : "platforms/",
        testbeds            : "testbeds/",
        oauth               : ("http://api.cotefe.net/oauth2/auth?client_id=4e0e8af627594856a726b81c5c9f68f2&redirect"),
        me                  : "me",
        redirect            : "http://localhost:8080/htmls/getdata.html&response_type=token",        
        comment             : "JS configuration ",
        localUser           : "_cotefeUser",
        localUserProject    : "_coetfeProject",
        localUserExperiment : "_cotefeExperiments",
        localUserJobs       : "_cotefeJobs",
        localUserPlatform   : "_cotefePlatforms",
        localUserTestBeds   : "_cotefeTestBeds",        
        link                : function(path){return this.apiUri+"/"+path+"";},
        linkTok             : function(path,token){return (this.link(path)+"?access_token="+token);},
        log                 : function(value){console.log(value);},
        token               :"",
    };


/*
 * ajax events and response handlers
 */
cotefe.newRequest =function()
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
cotefe.ajax_request = function(params){
        params.method = ( params.method ? params.method : 'GET');
        params.payload= ( params.payload ? params.payload: null);
        var request = new cotefe.newRequest();
        request.onreadystatechange = function(){
            if(request.readyState == 4){
                if(request.status == 200){
                    params.onComplete(request)
                }else
                {
                    params.onComplete(request)
                }
            }
        }
        request.open(params.method, params.url);
        request.send(params.payload);
    }
cotefe.getAjaxResponse = function(params)
{
    return params.responseText;
}
cotefe.getAjaxStatus = function(params)
{
    return params.status;
}

/*
 * session storage handler
 */
cotefe.session=function(){};
cotefe.session.create=function(){
    
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
cotefe.session.write=function(key,value)
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




/*
 * on first load get all data and save to session
 * 1. save user info with token
 * 2. get user projects list
 * 3. get user each project and save in session
 * 5. repeat 2 and 3 for experiment and job
 * 6. get platforms and test-beds
 * 7. once done send user to his dash-board
 */

cotefe.application={};
cotefe.application.generator={token:cotefe.token};
/*
 * 1 getting user me
 */
cotefe.application.getUserInfo=function(token,type)
                                {
                                      return {method:"GET",url:(cotefe.linkTok(type,token)),onComplete:function(result){cotefe.application.onMeDone(token,type,result)}};                                       
                                };
/*
 * 2 set user in storage
 */
cotefe.application.onMeDone=function(token,type,data)
                            {                               
                                if(cotefe.getAjaxStatus(data) == 200)
                                {
                                    var obj=JSON.parse(cotefe.getAjaxResponse(data));
                                    cotefe.log(obj);
                                    obj.session=access_token;
                                    var jsonA=JSON.stringify(obj);
                                    if(cotefe.session.create())
                                    {
                                        cotefe.session.write(cotefe.localUser,jsonA);
                                        cotefe.log("User Written");                                                                            
                                    }
                                    else
                                    {
                                        console.log("Session Failed");
                                    }
                                }
                                else
                                {
                                    alert("There was some problem by Login.Please try again later!!"+cotefe.getAjaxStatus(data));
                                    document.location.href=cotefe.mainUri;
                                }                                
                            };           

/*
 * 3 get project called 
 */
                