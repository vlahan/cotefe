

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
