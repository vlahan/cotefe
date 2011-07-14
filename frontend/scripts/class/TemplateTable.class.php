<?php

class CreateTable{
	var $headers;
	var $recordes;
	var $title;
	
	function CreateTable($title,$headers,$recordes)
	{
		$this->title=$title;
		$this->headers=$headers;
		$this->recordes=$recordes;
	}
	
	function generateTitle()
	{
		return "<h3>".$this->title."</h3>";
	}
	
	function generateHeads()
	{
		$th="<tr>";
		if(!empty($this->headers))
		{
			foreach($this->headers as $key=>$value)
			{
				$th.="<th ".$value['attribute']." >".$value['text']."</th>";
			}
			return $th.'</tr>';
		}
		else
		{	return $th;}
		
	}
	
	function addRecords()
	{
		$td="";
		if(!empty($this->recordes))
		{
			
			foreach($this->recordes as $record)
			{
				$td.="<tr>";
				foreach($record as $item)
				{
					if(!isset($item['attribute']))
					{
						if(!isset($item['a']))
							{$td.="<td  >".$item['text']."</td>";}
						else
							{$td.="<td  ><a href='".$item['a']."'>".$item['text']."</a></td>";	}
					}
					else
					{
						if(!isset($item['a']))
						{	$td.="<td ".$item['attribute']." >".$item['text']."</td>";}
						else
						{$td.="<td ".$item['attribute']." ><a href='".$item['a']."'>".$item['text']."</a></td>";}
					}
				}
				$td.="</tr>";
				
			}
			return $td;
		}
		else
		{	return $td;}
	}
	
	function render()
	{
		return $this->generateTitle().'<table cellspacing="0" class="table-list"'.$this->generateHeads().$this->addRecords().'</table>';
	}
	
	
}


?>