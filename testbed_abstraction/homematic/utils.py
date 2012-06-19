

#To check whether a device in the devices list from CCU is present in the channels of sqlite!
def check_channel_presence(id, channels_list):
  for channel in channels_list:
    if(id == channel.id):
       return True
  return False

#To check whether a device in the devices list from CCU is present in the nodes of sqlite!
def check_node_presence(id, nodes_list):
  for node in nodes_list:
    if(id == node.id):
       return True
  return False

#To check whether a device in the devices list from CCU has it's parameter sets in sqlite!
def check_parameter_presence(chid, position_in_paramset, parameter_list):
  for parameter in parameter_list:
    if(parameter.id == chid+':'+str(position_in_paramset)):
       return True
  return False

#To check whether a channel from sqlite is present in the devices list from CCU!
def check_device_presence_for_channel(id, devices_list):
  for device in devices_list:
    parent = device['PARENT']
    if (parent!='' and parent!= 'BidCoS-RF') :
      device_address = device['ADDRESS']
      if(id == device_address):
         return True
  return False

#To check whether a node from sqlite is present in the devices list from CCU!
def check_device_presence_for_node(id, devices_list):
  for device in devices_list:
    parent = device['PARENT']
    if (parent!='' and parent!= 'BidCoS-RF') :
      if(id == parent):
         return True
  return False

#To check whether a parameter from sqlite has it's device present in the devices list from CCU!
def check_device_presence_for_parameter(id, device_list):
  for device in device_list:
    parent = device['PARENT']
    if (parent!='' and parent!= 'BidCoS-RF') :
      #splitting the parameter id to form the device address from the parameter id 
      pid_split = id.split(':')
      if(len(pid_split)>1):
        device_address_from_parameter = pid_split[0]+':'+pid_split[1]
        if(device['ADDRESS']==device_address_from_parameter):
          return True
  return False
 
#To check whether a channel is a sensor or not   
def check_sensor(address, parenttype):
  channel = address[-1:]
  if(parenttype=='HM-CC-SCD' or parenttype=='HM-CC-VD' or parenttype=='HM-Sec-MDIR' or parenttype=='HM-Sec-RHS' or parenttype=='HM-Sec-SC' or parenttype=='HM-Sec-Win' or parenttype=='HM-CC-TC'):
       return True
  return False

#To check whether a channel is an actuator or not   
def check_actuator(address, parenttype):
  channel = address[-1:]
  if(parenttype=='HM-CC-MDIR' or (parenttype=='HM-Sec-Win' and channel=='1') or (parenttype=='HM-CC-TC' and channel=='2')):
       return True
  return False

#We get the param as a string from the patch or put "input". This method returns the parameter of actual type after type casting
def get_type_casted_param(parameter_type,parameter_value_uncasted):
  if(parameter_type=='INTEGER'):
     parameter_value_casted = int(parameter_value_uncasted)
     return parameter_value_casted
  
  elif(parameter_type=='BOOL'):
     parameter_value_casted = bool(parameter_value_uncasted)

  elif(parameter_type=='FLOAT'):
     parameter_value_casted = float(parameter_value_uncasted)

  return parameter_value_casted

