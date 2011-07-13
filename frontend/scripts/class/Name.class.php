<?php
	
class Name
{
	public static function NameField($label,$value)
	{
		return "<tr><td>$label</td><td><input name='name' type='text' value='$value' /></td></tr>";
	}
	
}
?>