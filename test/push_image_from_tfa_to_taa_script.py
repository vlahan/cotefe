###############################################################################################           
################################## TO BE REMOVED - TEST ONLY ##################################
###############################################################################################

from google.appengine.ext import blobstore
from google.appengine.api import urlfetch

from poster.encode import multipart_encode, MultipartParam

SERVER_URL = 'http://localhost:8001'

h = httplib2.Http()

logging.info('getting the testbed resource...')
response, content = h.request(uri=SERVER_URL, method='GET', body='')
assert response.status == 200
logging.info('%d %s' % (response.status, response.reason))
testbed_dict = json.loads(content)
logging.debug(testbed_dict)

image_dict = {
        'name' : image.name,
        'description' : image.description,
    }
    
logging.info('creating a new image...')
response, content = h.request(uri=testbed_dict['images'], method='POST', body=json.dumps(image_dict))
assert response.status == 201
logging.info('%d %s' % (response.status, response.reason))
image_uri = response['content-location']
logging.debug(image_uri)

logging.info('getting the information about the image...')
response, content = h.request(uri=image_uri, method='GET', body='')
assert response.status == 200
logging.info('%d %s' % (response.status, response.reason))
image_dict= json.loads(content)
logging.debug(image_dict)

logging.info('uploading the actual image file...')

blob_key = image.file.file.blobstore_info.key()
blob_info = blobstore.BlobInfo(blob_key)
# blob_reader = blobstore.BlobReader(blob_key) # file object
# content = blobstore.fetch_data(blob_info, 0, blobstore.MAX_BLOB_FETCH_SIZE-1) # file content

params = []
params.append(MultipartParam(
    'imagefile',
    filename=image.file.name,
    filetype='application/octet-stream',
    value=blob_info))

datagen, headers = multipart_encode(params)

data = str().join(datagen)

result = urlfetch.fetch(
    url=image_dict['upload_to'],
    payload=data,
    method=urlfetch.POST,
    headers=headers,
    deadline=10)

logging.info('%d' % (result.status_code))


###############################################################################################           
################################## TO BE REMOVED - TEST ONLY ##################################
###############################################################################################