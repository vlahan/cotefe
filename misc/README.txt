## Installation ##

1. sudo apt-get install python-twisted-web python-setuptools python-yaml
2. sudo easy_install beanstalkc
3. You may also want to install and run a Beanstalkd server.

## Running ##

python beanrest.py

## Usage ##

GET /        = Global stats
GET /<tube>  = Tube stats
POST /<tube> = Put in tube

Easy way to test POST functionality:

curl -X POST -d "content-for-job" http://localhost/tube-for-job

## Limitations ##

* Only connects to the default Beanstalkd port on localhost.
