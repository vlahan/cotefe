

var cotefe=(function($){
 
	var config = {
        mainUri             : "http://localhost:8080",
        apiUri              : "https://api.cotefe.net",
        version             : 1.0,
        projects            : {uri:"/projects/",         session:"_cotefeProject",       message:"Project",      name:"projects"},
        experiments         : {uri:"/experiments/",      session:"_cotefeExperiments",   message:"Experiment",   name:"experiments"},
        jobs                : {uri:"/jobs/",             session:"_cotefeJobs",          message:"Job",          name:"jobs"},
        platforms           : {uri:"/platforms/",        session:"_cotefePlatforms"},
        testbeds            : {uri:"/testbeds/",         session:"_cotefeTestbeds"},
        images            	: {uri:"/images/",			 session:"_cotefeImages"},
        user                : {uri:"/me",                session:"_cotefeUser"},
        oauth               : "https://api.cotefe.net/oauth2/auth?client_id=4a9fb27ed6f94b64b40a1cab1c2f6929",       
        redirect            : "http://localhost:8080/htmls/dashboard.html&response_type=token",
        dashboard           : "/dashboard",        
        comment             : "JS configuration ",
        link                : function(path){return this.apiUri+"/"+path+"";},
        link2               : function(path,token){return (path+"?access_token="+token);},
        linkTok             : function(path,token){return (this.link(path)+"?access_token="+token);},
        log                 : function(value){console.log(value);},
        signOut             : function(){sessionStorage.clear();window.location.href=this.mainUri;},
        debug               : false,
        
        Resource  : Backbone.Model.extend({
				display: function(item,view) {
					this.fetch({
						success: function(model, response) {
							       new view({model:model});
			        				return (model);
			      				}
		    				});
		  				},
		  	
        			}),
        			
        ResourceList: Backbone.Collection.extend({display:function(item,view){	this.fetch({success: function(model,result) {new view({model:model});}})},
		 }),
       
    };
	
	
	
	return config;

})(jQuery)






