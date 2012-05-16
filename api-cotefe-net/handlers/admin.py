import webapp2

from models import Federation, Testbed, Platform, Sensor, Actuator, Interface

class DatastoreInitialization(webapp2.RequestHandler):

    def get(self):
        
        # cleaning the datastore
        # for user in User.all(): user.delete()
        
        # for identity in OpenIDIdentity.all(): identity.delete()  
        # for application in Application.all(): application.delete()
        # for session in OAuth2Session.all(): session.delete()
        
        for federation in Federation.all(): federation.delete()
        for testbed in Testbed.all(): testbed.delete()
        for platform in Platform.all(): platform.delete()
        for sensor in Sensor.all(): sensor.delete()
        for actuator in Actuator.all(): actuator.delete()
        for interface in Interface.all(): interface.delete()
        
        # for project in Project.all(): project.delete()
        # for experiment in Experiment.all(): experiment.delete()
        # for image in Image.all(): image.delete()
        # for property_set in PropertySet.all(): property_set.delete()
        # for virtual_node in VirtualNode.all(): virtual_node.delete()
        # for virtual_node_group in VirtualNodeGroup.all(): virtual_node_group.delete()
        # for virtual_task in VirtualTask.all(): virtual_task.delete()
        
        Federation(
            name = 'COTEFE',
            description = 'The goal of the CONET Testbed Federation (CTF) Task is to address some of these roadblocks by developing a software platform that will enable convenient access to the experimental resources of multiple testbeds organized in a federation of autonomous entities.',
        ).put()
        
        Testbed(
            key_name = 'twist',
            name = 'TWIST',
            description = 'The TKN Wireless Indoor Sensor network Testbed (TWIST), developed by the Telecommunication Networks Group (TKN) at the Technische Universitaet Berlin, is a scalable and flexible testbed architecture for experimenting with wireless sensor network applications in an indoor setting.',
            organization = 'TU Berlin',
            homepage = 'https://www.twist.tu-berlin.de:8000',
            server_url = 'https://www.twist.tu-berlin.de:8001',
            background_image_url = 'https://www.twist.tu-berlin.de:8001/uploads/testbed/background.jpg',
            coordinates_mapping_function_x = '-5.5+x*46.9+y+16.6',
            coordinates_mapping_function_y =  '1517-y*16.9-z*78.3',
        ).put()
        
        Testbed(
            key_name = 'wisebed',
            name = 'WISEBED',
            description = 'The WISEBED project is a joint effort of nine academic and research institutes across Europe.',
            organization = 'TU Delft',
            homepage = 'http://localhost',
            server_url = 'http://localhost',
        ).put()
        
        Platform(
            key_name = 'eyesifxv20',
            name = 'eyesIFXv20',
            description = '',
        ).put()
        
        Platform(
            key_name = 'eyesifxv21',
            name = 'eyesIFXv21',
            description = '',
        ).put()
        
        Platform(
            key_name = 'tmotesky',
            name = 'TmoteSky',
            description = '',
        ).put()
        
        Platform(
            key_name = 'telosa',
            name = 'TelosA',
            description = '',
        ).put()
        
        Platform(
            key_name = 'telosb',
            name = 'TelosB',
            description = '',
        ).put()
        
        Interface(
            key_name = 'tinyos',
            name = 'TinyOS',
            description = '',
        ).put()
        
        Interface(
            key_name = 'contiki',
            name = 'Contiki',
            description = '',
        ).put()
        
        Sensor(
            key_name = 'temperature',
            name = 'Temperature',
            description = '',
        ).put()
        
        Sensor(
            key_name = 'pressure',
            name = 'Pressure',
            description = '',
        ).put()
        
        Sensor(
            key_name = 'light',
            name = 'Light',
            description = '',
        ).put()
        
        Actuator(
            key_name = 'sound',
            name = 'Sound',
            description = '',
        ).put()
        
        Actuator(
            key_name = 'led',
            name = 'LED',
            description = '',
        ).put()
        
        self.response.out.write('Datastore has been initialized!')