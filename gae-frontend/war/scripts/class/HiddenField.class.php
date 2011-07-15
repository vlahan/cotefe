<?php
	
class HiddenField
{
	public static function HiddeBox($name,$value)
	{
		return "<input name='$name' type='hidden' value='$value' />";
	}
	
}
?>