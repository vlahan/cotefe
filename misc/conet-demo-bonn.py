import httplib2

http = httplib2.Http()

host = "127.0.0.1"
port = "8080"

username = "claudio.donzelli"
password = "password"

# HOW TO GET ALL JOBS

uri = "http://%s:%s/jobs/" % (host, port)
#Êuri = "http://www.google.com/"
method = "GET"
body = ""
headers = { "Accept" : "application/json;charset=UTF-8" }

response, content = http.request(uri, method, body, headers)

print response
print content

# HOW TO CREATE A NEW JOB

# POST /jobs/ HTTP/1.1
# Host: federation-server.appspot.com
# Content-Type: application/json;charset=UTF-8
# 
# {...new job...}
# 
# HTTP/1.1 201 Created
# Location: http://federation-server.appspot.com/jobs/123

# HOW TO GET A SINGE JOB

# GET /jobs/123 HTTP/1.1
# Host: federation-server.appspot.com
# Accept: application/json;charset=UTF-8
# 
# HTTP/1.1 200 OK
# Content-Type: application/json;charset=UTF-8
# 
# {...job 123...}

# HOW TO MODIFY INFORMATION ABOUT A JOB

# PUT /jobs/123 HTTP/1.1
# Host: federation-server.appspot.com
# Content-Type: application/json;charset=UTF-8
# 
# {...job 123 updated...}

# HTTP/1.1 200 OK
# Content-Type: application/json;charset=UTF-8
# 
# {...job 123 updated...}

# HOW TO DELETE A JOB

# DELETE /jobs/123 HTTP/1.1
# Host: federation-server.appspot.com
# Content-Type: application/json;charset=UTF-8
# 
# HTTP/1.1 200 OK
# 
# Content-Type: application/json;charset=UTF-8