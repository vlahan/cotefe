import httplib2

http = httplib2.Http()
response, content = http.request("http://127.0.0.1:8080/testbeds/123/jobs/")

print response
print content