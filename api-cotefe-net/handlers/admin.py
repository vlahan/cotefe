import webapp2

from models import *

class DatastoreInitialization(webapp2.RequestHandler):

    def get(self):
        
        # cleaning the datastore
        # for user in User.all(): user.delete()
        
        # for identity in OpenIDIdentity.all(): identity.delete()  
        # for application in Application.all(): application.delete()
        # for session in OAuth2Session.all(): session.delete()
        
        # for t in Testbed.all():    t.delete()
        # for p in Platform.all():   p.delete()
        
        # for project in Project.all(): project.delete()
        # for experiment in Experiment.all(): experiment.delete()
        # for image in Image.all(): image.delete()
        # for property_set in PropertySet.all(): property_set.delete()
        # for virtual_node in VirtualNode.all(): virtual_node.delete()
        # for virtual_node_group in VirtualNodeGroup.all(): virtual_node_group.delete()
        # for virtual_task in VirtualTask.all(): virtual_task.delete()
        
        Testbed(
            key_name = 'twist',
            name = 'TWIST',
            description = 'The TKN Wireless Indoor Sensor network Testbed (TWIST), developed by the Telecommunication Networks Group (TKN) at the Technische Universitaet Berlin, is a scalable and flexible testbed architecture for experimenting with wireless sensor network applications in an indoor setting.',
            organization = 'TU Berlin',
            homepage = 'https://www.twist.tu-berlin.de:8000',
            server_url = 'https://www.twist.tu-berlin.de:8001',
        ).put()
        
        Testbed(
            key_name = 'wisebed',
            name = 'WISEBED',
            description = 'The WISEBED project is a joint effort of nine academic and research institutes across Europe.',
            organization = 'TU Delft',
            homepage = 'http://dutigw.st.ewi.tudelft.nl',
            server_url = 'https://http://dutigw.st.ewi.tudelft.nl:3264',
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
        
        Platform(
            key_name = 'gnode',
            name = 'GNode',
            description = '',
        ).put()
        
        Platform(
            key_name = 'tnode',
            name = 'TNode',
            description = '',
        ).put()

        self.response.out.write('Datastore has been initialized!')