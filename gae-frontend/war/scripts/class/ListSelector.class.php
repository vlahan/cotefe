<?php
	
class ListSelector
{
	public static function ListSelectorField($label,$name,$params,$selected)
	{
		$arr=$params;
		$select="<select name='$name' size='1'>";
		foreach($arr as $key=>$value)
		{
			if($key==$selected)
			{
				$select.="<option value='$key' selected>$value</option>";
			}
			else
			{
				$select.="<option value='$key'>$value</option>";
			}	
		}
		
		$select.="</select>";		
		return "<tr><td>$label</td><td>$select</td></tr>";
	}
	
}
?>