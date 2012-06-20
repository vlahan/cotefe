from collections import OrderedDict

from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError, Http404
from django.core.exceptions import ObjectDoesNotExist

from api import config
from twist.config import XMLRPC_PROTOCOL, XMLRPC_USERNAME, XMLRPC_PASSWORD, XMLRPC_HOST, XMLRPC_PORT
from testbed_abstraction import utils
from twist.proxy import TWISTProxy
from homematic.proxy import HomeMaticProxy
from homematic.config import HOMEMATIC_CCU_URL
from homematic.utils import *

from api.models import Platform, Node, Channel, Parameter

twist_proxy = TWISTProxy(
    '%s://%s:%s@%s:%s' % (
        XMLRPC_PROTOCOL,
        XMLRPC_USERNAME,
        XMLRPC_PASSWORD,
        XMLRPC_HOST,
        XMLRPC_PORT
    )
)

homematic_proxy = HomeMaticProxy(HOMEMATIC_CCU_URL)

def testbed_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':
        
        resource = OrderedDict()
        resource['uri'] = config.SERVER_URL+'/'
        resource['media_type'] = config.MEDIA_TYPE
        resource['name'] = config.TESTBED_NAME
        resource['organization'] = config.TESTBED_ORGANIZATION
        resource['city'] = config.TESTBED_CITY
        resource['country'] = config.TESTBED_COUNTRY
        resource['nodes'] = config.SERVER_URL+'/nodes/'
        resource['jobs'] = config.SERVER_URL+'/jobs/'
        resource['images'] = config.SERVER_URL+'/images/'
        resource['users'] = config.SERVER_URL+'/users/'
        
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(utils.serialize(resource))
        return response
    
    if request.method == 'OPTIONS':
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response

    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
    
def platform_collection_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':
        
        platform_list = [ p.to_dict(head_only=True) for p in Platform.objects.all() ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(utils.serialize(platform_list))
        return response
    
    if request.method == 'OPTIONS':
        # 204
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
    
    else:
        # 405
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response

def node_collection_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':

        ########################################################
        #################      TWIST      ######################
        ########################################################
        
        try:
            native_node_list = twist_proxy.getAllNodes()
        except Exception:
            # 500
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        # updates or creates
        for native_node_dict in native_node_list:
            platform = Platform.objects.filter(native_id = native_node_dict['platform_id'])[0]              
            node, created = Node.objects.get_or_create(native_id = native_node_dict['node_id'],
                defaults = {
                    'id' : native_node_dict['serial'],
                    'name' : 'WSN node',
                    'native_id' : native_node_dict['node_id'],
                    'platform' : platform,
                    'location_x' : native_node_dict['location_x'],
                    'location_y' : native_node_dict['location_y'],
                    'location_z' : native_node_dict['location_z'],
                    
                }
            )
        
        # delete nodes that are not present in the native database
        native_node_id_list = [ native_resource_dict['node_id'] for native_resource_dict in native_node_list ]
        Node.objects.exclude(native_id__in = native_node_id_list).delete()
        
        ########################################################
        ################    END OF TWIST   #####################
        ########################################################
        
        ########################################################
        ################    HOMEMATIC      #####################
        ########################################################
        
        # Getting the list of all channels, nodes,parameters from the sqlite and devices from CCU
        
        platform = Platform.objects.get(id = 'homematic')
        
        device_list = homematic_proxy.listDevices()
        
        node_list = Node.objects.all().filter(platform = platform)
        channel_list = Channel.objects.all()
        parameter_list = Parameter.objects.all()
        
        # Adding the nodes to a set inorder to avoid adding same node multiple times into sqlite
        hmnodes = set()
        
        # Adding the new nodes and channels which are not present in the Django sqlite database
        for n in device_list:
            
            parent = n['PARENT']
            
            if (parent!='' and parent!= 'BidCoS-RF'):

                #Getting the paramset description and the paramset for each device
                paramset = homematic_proxy.getParamset(n['ADDRESS'],"VALUES")
                paramset_description = homematic_proxy.getParamsetDescription(n['ADDRESS'],"VALUES")

                # Adding new nodes
                if not check_node_presence(parent, node_list):
                    if (parent not in hmnodes):
                        hmnodes.add(parent)
                        node = Node(
                            id = parent,
                            name = n['PARENT_TYPE'],
                            platform = platform) 
                        node.save()
                        
                #Adding new channels
                if not check_channel_presence(n['ADDRESS'], channel_list):
                    assign_node = Node.objects.get(id = parent)
                    sensor_status = check_sensor(n['ADDRESS'],assign_node.name)
                    actuator_status = check_actuator(n['ADDRESS'],assign_node.name)
                    channel = Channel(id = n['ADDRESS'] , node = assign_node, name = n['TYPE'], is_sensor=sensor_status, is_actuator= actuator_status)
                    channel.save()
                    
                #Adding Parameters
                position_in_paramset = 0
                for parameter in paramset_description:
                    if((parameter in paramset)==True):
                        if not check_parameter_presence(n['ADDRESS'], position_in_paramset, parameter_list):
                            assign_channel = Channel.objects.get(id=n['ADDRESS'])
                            min_value = paramset_description[parameter]['MIN']
                            max_value = paramset_description[parameter]['MAX']
                            punit = paramset_description[parameter]['UNIT']
                            ptype = paramset_description[parameter]['TYPE']
                            pid = '%s:%d' % (assign_channel.id,position_in_paramset)
                            pname = paramset_description[parameter]['ID']
                            pvalue = homematic_proxy.getValue(n['ADDRESS'],parameter)
                            parameter_object = Parameter(id=pid, channel = assign_channel, min=min_value, max=max_value, unit = punit, value=pvalue, type= ptype, name = pname)
                            parameter_object.save()
                    position_in_paramset = position_in_paramset + 1

        # Getting the list of channels and nodes from sqlite after the above updation 
        channel_list = Channel.objects.all()
        node_list = Node.objects.filter(platform = platform)
        parameter_list = Parameter.objects.all()

        # Deleting the channels which are not present in actual devices list but shown out in sqlite
        for channel in channel_list:
            if not check_device_presence_for_channel(channel.id, device_list):
                channel.delete()
                
        # Deleting the nodes which are not present in actual devices list but shown out in sqlite 
        for node in node_list:
            if not check_device_presence_for_node(node.id, device_list):
                node.delete()

        # Deleting the parameters from sqlite for which the related device is not present in the device list from CCU
        for parameter in parameter_list:
            if not check_device_presence_for_parameter(parameter.id, device_list):
                parameter.delete()
        
        ########################################################
        ##############    END OF HOMEMATIC    ##################
        ########################################################
        
        # getting all the node models from the database
        nodes = Node.objects.all().order_by('location_x', 'location_y', 'location_z')
            
        # applying possible filters
        if 'native_id' in request.GET and not (request.GET['native_id'] is None):
            nodes = nodes.filter(native_id = request.GET['native_id'])
            
        if 'native_id__in' in request.GET and not (request.GET['native_id__in'] is None):
            nodes = nodes.filter(native_id__in = map(int, request.GET['native_id__in'].split(',')))
            
        if 'native_id__not_in' in request.GET and not (request.GET['native_id__not_in'] is None):
            nodes = nodes.exclude(native_id__in = map(int, request.GET['native_id__not_in'].split(',')))
        
        if 'platform' in request.GET and not (request.GET['platform'] is None):
            nodes = nodes.filter(platform = Platform.objects.get(id = request.GET['platform']))
            
#        if 'image' in request.GET and not (request.GET['image'] is None):
#            nodes = nodes.filter(image = Image.objects.get(id = request.GET['image']))
            
        if 'n' in request.GET and not (request.GET['n'] is None):
            nodes = nodes[:request.GET['n']]
        
        # exporting the list of node models into a list of dictionaries  
        nodes = [ n.to_dict(head_only = True) for n in nodes ]
        
        # logging.warning('NUMBER OF NODES RETURNED: %d' % len(nodes))
        
        # generating 200 response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        
        ############### CACHING #################
        
        from wsgiref.handlers import format_date_time
        import datetime
        from time import mktime
        
        now = datetime.datetime.now()
        expires = now + datetime.timedelta(0, 3600)
        stamp = mktime(expires.timetuple())

        response['Expires'] = format_date_time(stamp)
        response['Cache-control'] = 'max-age=3600, must-revalidate'
        
        ############### CACHING #################
        
        response.write(utils.serialize(nodes))
        return response
    
    if request.method == 'OPTIONS':
        # 204
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
    
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def node_resource_handler(request, node_id):
    
    allowed_methods = ['GET']
    
    try:
        node = Node.objects.get(id = node_id)
    
    except ObjectDoesNotExist:
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
                
        try:            
            
            if node.platform.id == 'homematic':
                
                # Getting the devices list from CCU
                device_list = homematic_proxy.listDevices()
                # Checking whether the node is still connected. (cross checking the sqlite result with CCU device list)
                assert check_device_presence_for_node(node.id, device_list)
            
            else:
                
                # getting nodes from TWIST
                twist_proxy.getNode(node.native_id)[0]
            
        except Exception:
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
    
        # node.name = 'WSN node'
        # node.platform = Platform.objects.filter(native_id = native_node_dict['platform_id'])[0]
        # node.save()
        
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(utils.serialize(node.to_dict()))
        return response
    
    if request.method == 'OPTIONS':
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
        
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
    
def node_channel_collection_handler(request, nodeid):
    
    if request.method == 'GET':

        # Getting the list of all channels
        channels = Channel.objects.all().filter(node = Node.objects.get(id = nodeid))
        
        # applying possible filters
        if 'type' in request.GET and not (request.GET['type'] is None):
            
            if request.GET['type'] == 'sensor':
                channels = channels.filter(is_sensor = True)
                
            elif request.GET['type'] == 'actuator':
                channels = channels.filter(is_actuator = True)
            
            else:
                pass
            
        # Getting the devices list from CCU
        device_list = homematic_proxy.listDevices()
        channel_list = list()
        
        for ch in channels:
            # Checking whether the channel is still present. (cross checking the sqlite result with CCU device list)
            if(check_device_presence_for_channel(ch.id, device_list)):
                channel_list.append(ch.to_dict(head_only=True))

            else:
                ch.delete()
        
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(utils.serialize(channel_list))
        return response


def node_channel_resource_handler(request, nodeid, channelid):
    
    if request.method == 'GET':
        # Getting the devices list from CCU
        device_list = homematic_proxy.listDevices()
        # Getting the channel from sqlite

        try:
            channel = Channel.objects.get(id = '%s:%s' % (nodeid, channelid))
        except Channel.DoesNotExist:
            raise Http404   
                   
        # Checking whether the channel is still present. (cross checking the sqlite result with CCU device list)
        try:
            if(check_device_presence_for_channel(channel.id, device_list)):        
                # Forming httpresponse 
                response = HttpResponse()
                response['Content-Type'] = 'application/json'
                cdict = channel.to_dict()
                response.write(utils.serialize(cdict))
                return response
            else:
                channel.delete()
        except :
            raise Http404

    
def channel_parameter_collection_handler(request, nodeid, channelid):

    if request.method == 'GET':

        # Getting the list of all parameters from SQLite!
        parameters = Parameter.objects.all().filter(channel = Channel.objects.get(id = nodeid+':'+channelid))
        # Getting the devices list from CCU
        device_list = homematic_proxy.listDevices()
        parameter_list = list()
        for parameter in parameters:
            #Checking whether the device with corresponding parameters is still present in the CCU Devices list
            if(check_device_presence_for_parameter(parameter.id, device_list)):
                pvalue = homematic_proxy.getValue(parameter.channel.id,parameter.name)
                parameter.value = float(pvalue)
                parameter.save()
                parameter_list.append(parameter.to_dict(head_only=True))
            else:
                parameter.delete()

        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(utils.serialize(parameter_list))
        return response

def channel_parameter_resource_handler(request, nodeid, channelid, parameterid):
    allowed_methods = ['GET', 'PATCH', 'PUT']

    if request.method == 'GET':
        # Getting the devices list from CCU
        device_list = homematic_proxy.listDevices()
        # Getting the parameter from sqlite

        try:
            parameter = Parameter.objects.get(id = '%s:%s:%s' % (nodeid, channelid, parameterid))

        except Channel.DoesNotExist:
            raise Http404   
                   
        # Checking whether the device correspoding to the parameter is still present in devices list from CCU.
        try:
            if(check_device_presence_for_parameter(parameter.id, device_list)):        
                # Forming httpresponse 
                pvalue = homematic_proxy.getValue(parameter.channel.id,parameter.name)
                parameter.value = float(pvalue)
                parameter.save()
                response = HttpResponse()
                response['Content-Type'] = 'application/json'
                pdict = parameter.to_dict()
                response.write(utils.serialize(pdict))
                return response
            else:
                parameter.delete()
        except :
            raise Http404    

    if request.method == 'PATCH':
        #Getting the json object from the request
        channel_parameter_json = request.raw_post_data
        
        try:
            #Converting the json object to dictionary
            channel_parameter_dict = utils.deserialize(channel_parameter_json)
            #Retrieving the parameter object from the SQLite
            parameter = Parameter.objects.get(id = '%s:%s:%s' % (nodeid, channelid, parameterid))
            #Changing the value of the parameter object and saving it back
            parameter_value = channel_parameter_dict['value']
            parameter.value = float(parameter_value)
            parameter.save()
            type_casted_pvalue = get_type_casted_param(parameter.type, parameter_value)
            homematic_proxy.setValue(parameter.channel.id,parameter.name,type_casted_pvalue)
            # generate response
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(utils.serialize(parameter.to_dict()))
            return response
            
        except Exception:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response

    if request.method == 'PUT':
        #Getting the json object from the request
        parameter_json = request.raw_post_data
        try:
            #Converting the json object to dictionary
            channel_parameter_dict = utils.deserialize(parameter_json)
            #Retrieving the parameter object from the SQLite
            parameter = Parameter.objects.get(id = '%s:%s:%s' % (nodeid, channelid, parameterid))
            #Changing the attributes of the parameter object and saving it back
            parameter_value = channel_parameter_dict['value']
            parameter.value   = float(parameter_value)
            parameter.name    = channel_parameter_dict['name']
            parameter.id      = channel_parameter_dict['id']
            parameter.unit    = channel_parameter_dict['unit']
            min_value = channel_parameter_dict['min']
            max_value = channel_parameter_dict['max']
            parameter.min    = float(min_value)
            parameter.max     = float(max_value)
            parameter.save()
            type_casted_pvalue = get_type_casted_param(parameter.type, parameter_value)
            homematic_proxy.setValue(parameter.channel.id,parameter.name,type_casted_pvalue)
            # generate response
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(utils.serialize(parameter.to_dict()))
            return response
            
        except Exception:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response



#def nodegroup_collection_handler(request):
#    
#    allowed_methods = ['GET', 'POST']
#    
#    if request.method == 'GET':
#        
#        nodegroups = [ nodegroup.to_dict(head_only = True) for nodegroup in NodeGroup.objects.all() ]
#        
#        # generating 200 response
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write(utils.serialize(nodegroups))
#        return response
#    
#    if request.method == 'POST':
#        
#        try:
#            nodegroup_dict = utils.deserialize(request.raw_post_data)
#
#            nodegroup = NodeGroup(
#                name = nodegroup_dict['name'],
#                description = nodegroup_dict['description'],
#                job = Job.objects.get(id = nodegroup_dict['job'])
#            )
#            nodegroup.save()
#            
#            for node_id in nodegroup_dict['nodes']:
#                NodeGroup2Node.objects.get_or_create(nodegroup = nodegroup, node = Node.objects.get(id = node_id))
#            
#            # generate response
#            response = HttpResponse(status=201)
#            response['Location'] = nodegroup.get_absolute_url()
#            response['Content-Location'] = nodegroup.get_absolute_url()
#            response['Content-Type'] = 'application/json'
#            return response
#        except Exception:
#            # 400
#            response = HttpResponseBadRequest()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
#
#    else:
#        response = HttpResponseNotAllowed(allowed_methods)
#        del response['Content-Type']
#        return response
#    
#def nodegroup_resource_handler(request, nodegroup_id):
#    
#    allowed_methods = ['GET', 'PUT', 'DELETE']
#    
#    try:
#        nodegroup = NodeGroup.objects.get(id = nodegroup_id)
#    
#    except ObjectDoesNotExist:
#        # 404
#        response = HttpResponseNotFound()
#        response['Content-Type'] = 'application/json'
#        return response
#    
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
#    
#    if request.method == 'GET':
#        # 200
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write(utils.serialize(nodegroup.to_dict()))
#        return response
#    
#    if request.method == 'PUT':
#        
#        nodegroup_json = request.raw_post_data
#        
#        try:
#            nodegroup_dict = utils.deserialize(nodegroup_json)
#
#            nodegroup.name = nodegroup_dict['name']
#            nodegroup.description = nodegroup_dict['description']
#            
#            nodegroup.save()
#            
#            # generate response
#            response = HttpResponse()
#            response['Content-Type'] = 'application/json'
#            response.write(utils.serialize(nodegroup.to_dict()))
#            return response
#            
#        except Exception:
#            # 400
#            response = HttpResponseBadRequest()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#    if request.method == 'DELETE':
#        
#        nodegroup.delete()
#        
#        # generate response
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        return response
#        
#    else:
#        response = HttpResponseNotAllowed(allowed_methods)
#        del response['Content-Type']
#        return response
#
#def job_collection_handler(request):
#    
#    allowed_methods = ['GET', 'POST']
#    
#    if request.method == 'GET':
#        
#        try:
#            native_job_list = proxy.getAllJobs()
#        except Exception:
#            # 500
#            response = HttpResponseServerError()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#        # updates or creates
#        for native_job_dict in native_job_list:
#            
#            resource_model, created = Job.objects.get_or_create(native_id = native_job_dict['job_id'],
#                defaults = {
#                    'native_id' : native_job_dict['job_id'],
#                    'native_platform_id_list' : ','.join(map(str,native_job_dict['resources'])),
#                    'name' : '(native job)',
#                    'description' : native_job_dict['description'],
#                    'datetime_from' : utils.utc_string_to_utc_datetime(native_job_dict['time_begin']),
#                    'datetime_to' : utils.utc_string_to_utc_datetime(native_job_dict['time_end']),
#                }
#            )
#            if not created:
#                resource_model.description = native_job_dict['description']
#                resource_model.time_begin = utils.utc_string_to_utc_datetime(native_job_dict['time_begin'])
#                resource_model.time_end = utils.utc_string_to_utc_datetime(native_job_dict['time_end'])
#                resource_model.save()
#        
#        # delete nodes that are not present in the native database
#        native_resource_id_list = [ native_resource_dict['job_id'] for native_resource_dict in native_job_list ]
#        Job.objects.exclude(native_id__in = native_resource_id_list).delete()
#        
#        jobs = Job.objects.all().order_by('datetime_from')
#        
#        if 'date_from' in request.GET and not (request.GET['date_from'] is None):
#            datetime_from = request.GET['date_from'] + 'T00:00:00+0000'
#            jobs = jobs.filter(datetime_from__gte = utils.utc_string_to_utc_datetime(datetime_from))
#            
#        if 'date_to' in request.GET and not (request.GET['date_to'] is None):
#            datetime_to = request.GET['date_to'] + 'T23:59:59+0000'
#            jobs = jobs.filter(datetime_to__lte = utils.utc_string_to_utc_datetime(datetime_to))
#
#        job_list = [ resource_model.to_dict(head_only = True) for resource_model in jobs ]
#        
#        # generating 200 response
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write(utils.serialize(job_list))
#        return response
#    
#    if request.method == 'POST':
#        
#        try:
#            job_dict = utils.deserialize(request.raw_post_data)
#            
#            if ('nodes' in job_dict) and not (job_dict['nodes'] is None):
#                node_id_list = job_dict['nodes']
#                
#            platform_native_id_set = set()
#            for node_id in node_id_list:
#                node = Node.objects.get(id = node_id)
#                platform_native_id_set.add(node.platform.native_id)
#            
#            native_job_dict = dict()
#            native_job_dict['description'] = job_dict['description']
#            native_job_dict['time_begin'] = job_dict['datetime_from']
#            native_job_dict['time_end'] = job_dict['datetime_to']
#            native_job_dict['resources'] = list(platform_native_id_set)
#            
#            try:
#                created_job_id_list = proxy.createJob(native_job_dict)
#                if len(created_job_id_list) == 0:
#                    raise None
#            except Exception:
#                # 500
#                response = HttpResponseServerError()
#                response['Content-Type'] = 'application/json'
#                return response
#            
#            job = Job(
#                name = job_dict['name'],
#                description = job_dict['description'],
#                datetime_from = utils.utc_string_to_utc_datetime(job_dict['datetime_from']),
#                datetime_to = utils.utc_string_to_utc_datetime(job_dict['datetime_to']),
#                native_id = created_job_id_list[0]['job_id'])
#            job.save()
#            
#            for node_id in node_id_list:
#                Job2Node(job = job, node = Node.objects.get(id = node_id)).save()
#                
#            # generate response
#            response = HttpResponse(status=201)
#            response['Location'] = job.get_absolute_url()
#            response['Content-Location'] = job.get_absolute_url()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#        except Exception:
#            # 400
#            response = HttpResponseBadRequest()
#            response['Content-Type'] = 'application/json'
#            return response
#    
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
#
#    else:
#        response = HttpResponseNotAllowed(allowed_methods)
#        del response['Content-Type']
#        return response
#
#def job_resource_handler(request, job_id):
#    
#    allowed_methods = ['GET', 'PUT', 'DELETE']
#    
#    if job_id == 'current':
#        try:
#            
#            from datetime import datetime
#            dt_now_utc = datetime.utcnow()
#            
#            job = Job.objects.filter(datetime_from__lt = dt_now_utc).filter(datetime_to__gt = dt_now_utc)[0]
#            
#            response = HttpResponse()
#            response['Content-Type'] = 'application/json'
#            response.write(utils.serialize(job.to_dict()))
#            return response
#        
#        except Exception:
#            # 404
#            response =  HttpResponseNotFound()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#    try:
#        job = Job.objects.get(id = job_id)
#    
#    except ObjectDoesNotExist:
#        # 404
#        response = HttpResponseNotFound()
#        response['Content-Type'] = 'application/json'
#        return response
#
#    if request.method == 'GET':
#        
#        try:
#            native_resource_list = proxy.getJob(job.native_id)
#            if len(native_resource_list) == 0:
#                # 404
#                response = HttpResponseNotFound()
#                response['Content-Type'] = 'application/json'
#                return response
#                
#        except Exception:
#            response = HttpResponseServerError()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#        native_resource_dict = native_resource_list[0]    
#        job.description = native_resource_dict['description']
#        job.datetime_from = utils.utc_string_to_utc_datetime(native_resource_dict['time_begin'])
#        job.datetime_to = utils.utc_string_to_utc_datetime(native_resource_dict['time_end'])
#            
#        job.save()
#        
#        # 200
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write(utils.serialize(job.to_dict()))
#        return response
#    
#    if request.method == 'PUT':
#
#        try:
#            job_dict = utils.deserialize(request.raw_post_data)
#            
#            if ('nodes' in job_dict) and not (job_dict['nodes'] is None):
#                node_id_list = job_dict['nodes']
#                
#            platform_native_id_set = set()
#            for node_id in node_id_list:
#                node = Node.objects.get(id = node_id)
#                platform_native_id_set.add(node.platform.native_id)
#                
#            native_job_dict = dict()
#            native_job_dict['job_id'] = job.native_id
#            native_job_dict['description'] = job_dict['description']
#            native_job_dict['time_begin'] = job_dict['datetime_from']
#            native_job_dict['time_end'] = job_dict['datetime_to']
#            native_job_dict['resources'] = list(platform_native_id_set)
#                
#            try:
#                proxy.updateJob(native_job_dict)
#            except Exception:
#                response = HttpResponseServerError()
#                response['Content-Type'] = 'application/json'
#                return response
#            
#            job.name = job_dict['name']
#            job.description = job_dict['description']
#            job.datetime_from = utils.utc_string_to_utc_datetime(job_dict['datetime_from'])
#            job.datetime_to = utils.utc_string_to_utc_datetime(job_dict['datetime_to'])
#            job.save()
#            
#            for node_id in node_id_list:
#                Job2Node(job = job, node = Node.objects.get(id = node_id)).save()
#
#            # 200
#            response = HttpResponse()
#            response['Content-Type'] = 'application/json'
#            response.write(utils.serialize(job.to_dict()))
#            return response
#            
#        except Exception:
#            # 400
#            response = HttpResponseBadRequest()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#    if request.method == 'DELETE':
#        
#        job.delete()
#        
#        try:
#            proxy.deleteJob(job.native_id)
#            
#        except Exception:
#            response = HttpResponseServerError()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#        # generate response
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        return response
#    
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
#        
#    else:
#        response = HttpResponseNotAllowed(allowed_methods)
#        del response['Content-Type']
#        return response
#
#def image_collection_handler(request):
#    
#    allowed_methods = ['GET', 'POST']
#    
#    if request.method == 'GET':
#        
#        collection_list = [ resource_model.to_dict(head_only = True) for resource_model in Image.objects.all() ]
#        
#        # 200
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write(utils.serialize(collection_list))
#        return response
#    
#    if request.method == 'POST':
#                
#        try:
#            image_dict = utils.deserialize(request.raw_post_data)
#            
#            image = Image(
#                name = image_dict['name'],
#                description = image_dict['description']
#            )
#            
#            image.save()
#            
#            # 201
#            response = HttpResponse(status=201)
#            response['Location'] = image.get_absolute_url()
#            response['Content-Location'] = image.get_absolute_url()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#        except Exception:
#            # 400
#            response = HttpResponseBadRequest()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
#
#    else:
#        response = HttpResponseNotAllowed(allowed_methods)
#        del response['Content-Type']
#        return response
#    
#def image_resource_handler(request, image_id):
#    
#    allowed_methods = ['GET', 'PUT', 'DELETE']
#    
#    try:
#        image = Image.objects.get(id = image_id)
#    
#    except ObjectDoesNotExist:
#        # 404
#        response = HttpResponseNotFound()
#        response['Content-Type'] = 'application/json'
#        return response
#
#    if request.method == 'GET':
#        # 200
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write(utils.serialize(image.to_dict()))
#        return response
#    
#    if request.method == 'PUT':
#        
#        try:
#            image_dict = utils.deserialize(request.raw_post_data)
#
#            image.name = image_dict['name']
#            image.description = image_dict['description']
#            
#            image.save()
#            
#            # 200
#            response = HttpResponse()
#            response['Content-Type'] = 'application/json'
#            response.write(utils.serialize(image.to_dict()))
#            return response
#            
#        except Exception:
#            # 400
#            response = HttpResponseBadRequest()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#    if request.method == 'DELETE':
#        
#        image.file.delete()
#        
#        image.delete()
#        
#        # generate response
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        return response
#    
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
#        
#    else:
#        response = HttpResponseNotAllowed(allowed_methods)
#        del response['Content-Type']
#        return response
#    
#
#def imagefile_upload_handler(request, image_id):
#    
#    allowed_methods = ['POST']
#      
#    if request.method == 'POST':
#                
#        try:
#            imagefile = request.FILES['imagefile']
#            
#            image = Image.objects.get(id = image_id)
#            
#            image.file = imagefile            
#            image.save()
#            
#            # 200
#            response = HttpResponse()
#            response['Content-Type'] = 'application/json'
#            response.write(utils.serialize(image.to_dict()))
#            return response
#        
#        except Exception:
#            # 400
#            response = HttpResponseBadRequest()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
#
#    else:
#        response = HttpResponseNotAllowed(allowed_methods)
#        del response['Content-Type']
#        return response
#    
#def burn_image_to_nodegroup_handler(request, nodegroup_id, image_id):
#    
#    allowed_methods = ['PUT']
#    
#    try:
#        nodegroup  = NodeGroup.objects.get(id = nodegroup_id)
#        image = Image.objects.get(id = image_id)
#    
#    except ObjectDoesNotExist:
#        # 404
#        response = HttpResponseNotFound()
#        response['Content-Type'] = 'application/json'
#        return response    
#        
#    if request.method == 'PUT':
#            
#        nodegroup.image = image
#        nodegroup.save()
#        
#        for ng2n in nodegroup.nodes.all():
#            ng2n.node.image = image
#            ng2n.node.save()
#
#        job_native_id = Job.objects.get(id = nodegroup.job).native_id
#        node_native_id_list = [ ng2n.node.native_id for ng2n in nodegroup.nodes.all() ]
#        image_path = image.file.file.name
#        
#        status = Status(
#            http_request = '%s %s' % (request.method, request.path_info),
#            status = 'running'
#        )
#        status.save()
#        
#        try:
#            result = proxy.burnImageToNodeList(status.id, job_native_id, node_native_id_list, image_path)
#            logging.warning(result)
#            
#        except Exception:
#            # 500
#            response = HttpResponseServerError()
#            response['Content-Type'] = 'application/json'
#            return response
#         
#        # generate response
#        response = HttpResponse(status = 202)
#        response['Content-Type'] = 'application/json'
#        response['Location'] = status.get_absolute_url()
#        return response
#    
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
#        
#    else:
#        response = HttpResponseNotAllowed(allowed_methods)
#        del response['Content-Type']
#        return response
#    
#def erase_image_to_nodegroup_handler(request, nodegroup_id):
#    
#    allowed_methods = ['DELETE']
#    
#    try:
#        nodegroup  = NodeGroup.objects.get(id = nodegroup_id)
#    
#    except ObjectDoesNotExist:
#        # 404
#        response = HttpResponseNotFound()
#        response['Content-Type'] = 'application/json'
#        return response
#        
#    if request.method == 'DELETE':
#        
#        nodegroup.image = None
#        nodegroup.save()
#        
#        for ng2n in nodegroup.nodes.all():
#            ng2n.node.image = None
#            ng2n.node.save()
#
#        job_native_id = Job.objects.get(id = nodegroup.job).native_id
#        node_native_id_list = [ ng2n.node.native_id for ng2n in nodegroup.nodes.all() ]
#        
#        status = Status(
#            http_request = '%s %s' % (request.method, request.path_info),
#            status = 'running'
#        )
#        status.save()
#        
#        try:
#            result = proxy.eraseImageFromNodeList(status.id, job_native_id, node_native_id_list)
#            logging.warning(result)
#            
#        except Exception:
#            # 500
#            response = HttpResponseServerError()
#            response['Content-Type'] = 'application/json'
#            return response
#         
#        # generate response
#        response = HttpResponse(status=202)
#        response['Content-Type'] = 'application/json'
#        response['Location'] = status.get_absolute_url()
#        return response
#    
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
#        
#    else:
#        response = HttpResponseNotAllowed(allowed_methods)
#        del response['Content-Type']
#        return response
#    
#    
#def status_collection_handler(request):
#    
#    allowed_methods = ['GET']
#
#    if request.method == 'GET':
#        
#        statuses = Status.objects.all().order_by('datetime_created')
#        
#        # 200
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write(utils.serialize(statuses))
#        return response
#    
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
#        
#    else:
#        response = HttpResponseNotAllowed(allowed_methods)
#        del response['Content-Type']
#        return response
#    
#def status_resource_handler(request, status_id):
#    
#    allowed_methods = ['GET']
#    
#    try:
#        status = Status.objects.get(id = status_id)
#    
#    except ObjectDoesNotExist:
#        # 404
#        response = HttpResponseNotFound()
#        response['Content-Type'] = 'application/json'
#        return response
#
#    if request.method == 'GET':
#        
#        if status.status == 'running':
#        
#            try:
#                result = proxy.isRequestPending(status_id)
#                logging.warning(result)
#                
#            except Exception:
#                # 500
#                response = HttpResponseServerError()
#                response['Content-Type'] = 'application/json'
#                return response
#        
#            if not result:            
#                status.status = 'completed'
#                status.save()
#        
#        # 200
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write(utils.serialize(status.to_dict()))
#        return response
#        
#    
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
#        
#    else:
#        response = HttpResponseNotAllowed(allowed_methods)
#        del response['Content-Type']
#        return response
#    
#def robot_resource_handler(request):
#    
#    allowed_methods = ['GET', 'PATCH']
#    
#    if request.method == 'GET':
#        
#        try:
#            (x, y, z) = proxy.getRobotPosition(1000)
#                            
#        except Exception:
#            response = HttpResponseServerError()
#            response['Content-Type'] = 'application/json'
#            return response
#        
#        robot = Node(
#            id = '4dd1ba50',
#            native_id = 1000,
#            name = 'Turtlebot',
#            platform = Platform.objects.get(id='Roomba'),
#            image = None,
#            location_x = x,
#            location_y = y,
#            location_z = z
#        )
#        
#        # 200
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write(utils.serialize(robot.to_dict()))
#        return response
#    
#    if request.method == 'PATCH':
#
#        try:
#            robot_dict = utils.deserialize(request.raw_post_data)
#            
#            x = robot_dict['location_x']
#            y = robot_dict['location_y']
#            z = robot_dict['location_z']
#                
#            try:
#                proxy.setRobotPosition(1000, x, y, z)
#                            
#            except Exception:
#                response = HttpResponseServerError()
#                response['Content-Type'] = 'application/json'
#                return response
#            
#            robot = Node(
#                id = '4dd1ba50',
#                native_id = 1000,
#                name = 'Turtlebot',
#                platform = Platform.objects.get(id='Roomba'),
#                image = None,
#                location_x = decimal.Decimal(x),
#                location_y = decimal.Decimal(y),
#                location_z = decimal.Decimal(z)
#            )
#            
#            # 200
#            response = HttpResponse()
#            response['Content-Type'] = 'application/json'
#            response.write(utils.serialize(robot.to_dict()))
#            return response
#            
#        except Exception:
#            # 400
#            response = HttpResponseBadRequest()
#            response['Content-Type'] = 'application/json'
#            return response
#    
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
    
    

    
