import xmlrpclib

# TESTBED XMLRPC PROXY IMPLEMENTED AS SINGLETON

class TestbedProxy(xmlrpclib.ServerProxy):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TestbedProxy, cls).__new__(cls, *args, **kwargs)