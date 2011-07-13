<?php
	
class Description
{
	public static function DescriptionField($label,$value)
	{
		return "<tr><td valign='top' >$label</td><td><textarea name='description'>$value</textarea></td></tr>";
	}
	
}
?>