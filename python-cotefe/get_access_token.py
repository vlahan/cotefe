from cotefe.client import COTEFEAPI

#client_id = raw_input("Client ID: ").strip()
#client_secret = raw_input("Client Secret: ").strip()
#redirect_uri = raw_input("Redirect URI: ").strip()

client_id = '661b6d2134744642baae57f7aa535802'
client_secret = '661b6d2134744642baae57f7aa535802'
redirect_uri = 'http://localhost:8090/'

api = COTEFEAPI(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

redirect_uri = api.get_authorize_login_url()

print "Visit this page and authorize access in your browser:\n", redirect_uri

code = raw_input("Paste in code in query string after redirect: ").strip()

access_token = api.exchange_code_for_access_token(code)

print "access_token: ", access_token
