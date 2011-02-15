#Author: Federico Di Gregorio

from psycopg2 import *
from psycopg2 import _psycopg as _2psycopg
from psycopg2.extensions import register_type, UNICODE
from psycopg2.extras import RealDictConnection

del connect
def connect(*args, **kwargs):
    kwargs['connection_factory'] = RealDictConnection
    conn=_2psycopg.connect(*args, **kwargs)
    conn.set_client_encoding('UNICODE')
    return conn
    
register_type(UNICODE)

