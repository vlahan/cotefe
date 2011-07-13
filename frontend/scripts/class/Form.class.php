<?php
include_once 'Name.class.php';
include_once 'Description.class.php';
include_once 'ListSelector.class.php';
include_once 'TextField.class.php';
include_once 'HiddenField.class.php';
include_once 'EmptyTR.class.php';
include_once 'TemplateTable.class.php';

class Form
{
	public static function Header($title)
	{
		return "<h3>$title</h3>";
	}
	public static function FormStart()
	{
		return '<form method="POST"><table cellspacing="0" >';
	}
	
	public static function FormEnd()
	{
		return '</table></form>';
	}
	
	public static function FromSubmit($value)
	{
		return "<tr><td><input type='submit' value='$value' class='submitP'  /></td><td><input type='reset' value='Clear' /></td></tr>";
	}
	
	public static function GenerateForm()
	{
		echo self::FormStart();
		echo Name::NameField('Project : ', "");
		echo Description::DescriptionField('Project Description : ', "valzue");
		echo ListSelector::ListSelectorField('Project List:', 'project',array("Project1" => "Project1", "Project2" => "Project2", "Project3" => "Project3"));
		echo self::FromSubmit('Add Project');
		echo self::FormEnd();
	}
}


?>