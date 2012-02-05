/*
 * web scripts for events uses jquery engine
 */
jQuery(document).ready(function(){  
    init();
});

function init(){
        initSignOut();//add sign off event
        
        leftMenu();//initialize left-menu
        tabsEvent();//initialize tabs
        disableanchors();//disable all anchors to follow
        greetUser();//user info
        initDashboard();//create dash-board
    };

/*
 * sign off event
 */
function initSignOut()
{
    $("#signout").bind("click",function(event){event.preventDefault();cotefe.signOut();});
};

/*
 * disable all anchors in left menu and content
 */

function disableanchors()
{
    $("#sidebar, #content").on("click",function(event){event.preventDefault();event.stopPropagation();});
}

/*
 * left menu event add and handler
 */
function leftMenu()
{
    $("#nav a").click(function(event) {
          event.preventDefault();
          var ids=($(this).attr('id'));
          leftMenuActionHandler(ids);
    });
    $('#nav a').on("click",function(event) {$(this).next().toggle('fast');}).next().hide();   
}

function leftMenuActionHandler(selector)
{
    switch(selector)
    {
        case "dashboard"    :break;
        case "homescreen"   :initDashBoard();break;
        case "myaccount"    :break;
        case "settings"     :break;
        case "signout"      :signOut();break;
        case "projects"     :break;
        case "addP"         :addProject(null);break;
        case "listP"        :listProject();break;
        case "experiments"  :break;
        case "addE"         :break;
        case "listeE"       :break;
        case "jobs"         :break;
        case "addJ"         :break;
        case "listJ"        :break;     
        case "images"       :break;
        case "uploadIm"     :break;
        case "listIm"       :break;
    }
}

/*
 * tabs event
 */
function tabsEvent()
{
    $(".tab_content").hide(); 
    $("ul.tabs li:first").addClass("active").show(); 
    $(".tab_content:first").show(); 

    //On Click Event
    $("ul.tabs li").on("click",function(event) {
        
        $("ul.tabs li").removeClass("active"); 
        $(this).addClass("active"); 
        $(".tab_content").hide(); 

        var activeTab = $(this).find("a").attr("href");
        $(activeTab).fadeIn(); 
        return false;
    });
}


/*
 * user info
 */
function greetUser()
{
    var data=cotefe.application.user;
    
            menu = new EJS({url: '../templates/greetTemplate.ejs'}).render(data);
            var navi=document.getElementById("userWelcomeText");
            navi.innerHTML=menu;
}
function capitalize (text) {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

function initDashboard()
{
            numberOfItems=5;
            /*
             * image menu
             */
            var data={projects:"projects",experiments:"experiments",jobs:"jobs",images:"images"};    
            menu = new EJS({url: '../templates/imageMenu.ejs'}).render(data);
            
            /*
             * render project
             */
            cotefe.application.dumbObj=[];
            var arr=JSON.parse(sessionStorage.getItem(cotefe.localUserProject));
            for(i=0;i<arr.length;i++)
            {
                obj=JSON.parse(arr[0]);
                cotefe.application.dumbObj.push(obj)
            };
            data={
                    headings:['Project Name','Date','Edit','Delete'],
                    objects :cotefe.application.dumbObj,
                    len:numberOfItems
                 };
            table= new EJS({url: '../templates/tableModel.ejs'}).render(data);
            
            data={ imagedata:menu,projecttable:table};
            
            completepage = new EJS({url: '../templates/dashboard.ejs'}).render(data);
            var navi=document.getElementById("content");
            navi.innerHTML=completepage;            
            /*
             * render experiments
             */
            /*
             * render jobs
             */
            /*
             * render images
             */
            $(document).on("load",tabsEvent());
                 
}
