<?php
	
class TextField
{
	public static function TextBox($label,$name,$value)
	{
		return "<tr><td>$label</td><td><input name='$name' type='text' value='$value' /></td></tr>";
	}
	
}
?>