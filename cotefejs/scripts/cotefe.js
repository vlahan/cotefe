(function($) {
//////test
Model = Backbone.Model.extend();
ListAll= Backbone.View.extend({
	el : '#test' ,
	initialize : function() {  _.bindAll(this, "render");this.render(); },
	render : function() 
	{
    		$(this.el).append( _.template('bla bla',this.model.toJSON()));
    		return this;
  	}
  	
});



resource= Backbone.Model.extend({
		id:"https://api.cotefe.net/me?access_token=1908700504b2474e9e9d6cc6225d3ece",
		url:"https://api.cotefe.net/me?access_token=1908700504b2474e9e9d6cc6225d3ece",
 		display: function() {
	    this.fetch({
	      success: function(model, response) {
	        console.log(response);
	        console.log("***************************");
	        console.log(model.get('first'));
	      }
    });
  }
});


})(jQuery);

$(document).ready(function(){
   model = new Model({label:'Test label'});
   view = new ListAll({model: model});
   
   
   res= new resource();
   res.display();

	
	
	
	/*
	 * slide form divs
	 */
	$("h3").click(function(){$(this).next("form").slideToggle("slow");});

   
 });
