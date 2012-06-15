import xmlrpclib

# HOMEMATIC XMLRPC PROXY IMPLEMENTED AS SINGLETON

class HomeMaticProxy(xmlrpclib.ServerProxy):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HomeMaticProxy, cls).__new__(cls, *args, **kwargs)