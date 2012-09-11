#!/usr/bin/env python
#
# manage.py
#  Manage and run the bottlerocket server using Flask-script
#
# Created by Martin Bor <m.c.bor@tudelft.nl> on 2012-09-10
# Copyright (c) 2012 TU Delft. All rights reserved.
#

from flask.ext.script import Manager
from bottlerocket import app

manager = Manager(app)

if __name__ == '__main__':
	manager.run()

