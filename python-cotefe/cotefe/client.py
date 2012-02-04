import config
import oauth2
from models import *

class COTEFEAPI(oauth2.OAuth2API):
    
    protocol = "http"
    host = "api.cotefe.net"
    access_token_field = "access_token"
    authorize_url = "http://api.cotefe.net/oauth2/auth"
    access_token_url = "http://api.cotefe.net/oauth2/token"
    
    protocol = "http"
    host = "localhost:8080"
    access_token_field = "access_token"
    authorize_url = protocol + "://" + host + "/oauth2/auth"
    access_token_url = protocol + "://" + host + "/oauth2/token"