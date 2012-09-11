#
# __init__.py
#  
# Created by Martin Bor <m.c.bor@tudelft.nl> on 2012-09-10
# Copyright (c) 2012 TU Delft. All rights reserved.
#

from flask import Flask
app = Flask(__name__)
app.config.from_object('config')

import bottlerocket.views
from bottlerocket.database import db_session
from bottlerocket.proxy import wisebed_proxy

@app.teardown_request
def shutdown_session(exception=None):
	db_session.remove()

