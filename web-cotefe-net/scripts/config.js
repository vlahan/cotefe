/*
 * configuration file
 * "https://web.cotefe.net"
 */
 var cotefe = {
        mainUri             : "https://web.cotefe.net",
        apiUri              : "https://api.cotefe.net/",
        version             : 1.0,
        projects            : {uri:"projects/",         session:"_cotefeProject",       message:"Project",      name:"projects"},
        experiments         : {uri:"experiments/",      session:"_cotefeExperiments",   message:"Experiment",   name:"experiments"},
        jobs                : {uri:"jobs/",             session:"_cotefeJobs",          message:"Job",          name:"jobs"},
        platforms           : {uri:"platforms/",        session:"_cotefePlatforms"},
        testbeds            : {uri:"testbeds/",         session:"_cotefeTestbeds"},
        user                : {uri:"me",                session:"_cotefeUser"},
        oauth               : "https://api.cotefe.net/oauth2/auth?client_id=aba144033daa4826baf861686195c421",       
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
  *Resource  
  */
	Resource  = Backbone.Model.extend({
			display: function(item,view) {
			    this.fetch({
			      	success: function(model,response) {
			      			new view({el:item,model:model});
			        		return (model);
			      		}
		    		});
		  		}
		  	
	});
	
	ListView=Backbone.View.extend({
		initialize:function(){_.bindAll(this,"render");this.render();},
		render:function()
		{
			console.log(JSON.stringify(this.model,null,'\t'));
		}
	});
	
	User=Resource.extend({url:"https://api.cotefe.net/me?access_token=2d07d8ede77a4ff5aeef07553026deee"});	
	user= new User()
	user.display("item",ListView);