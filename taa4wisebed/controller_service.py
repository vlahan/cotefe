#!/usr/bin/env python
#
# controller_service.py
#  Service implementing the WISEBED Controller API. Receives
#  the responses to ansynchronous operations and stores them
#  in the database.
#
# Created by Martin Bor <m.c.bor@tudelft.nl> on 2012-09-10
# Copyright (c) 2012 TU Delft. All rights reserved.
#

import logging
import times

from spyne.application import Application
from spyne.decorator import srpc
from spyne.interface.wsdl import Wsdl11
from spyne.protocol.soap import Soap11
from spyne.service import ServiceBase

from spyne.model.primitive import String
from spyne.model.primitive import Integer
from spyne.model.primitive import DateTime
from spyne.model.binary import ByteArray
from spyne.model.complex import ComplexModel

from spyne.server.wsgi import WsgiApplication

from bottlerocket.database import db_session
from bottlerocket import models

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

class RequestId(String):
	__namespace__ = "urn:CommonTypes"
	pass

class Status(ComplexModel):
	__namespace__ = "urn:ControllerService"

	nodeId = String.customize(min_occurs=1, max_occurs=1, nillable=False)
	value = Integer.customize(min_occurs=0, max_occurs=1, nillable=False)
	msg = String.customize(min_occurs=0, max_occurs=1, nillable=False)

class RequestId(String):
	__namespace__ = "urn:CommonTypes"

class RequestStatus(ComplexModel):
	__namespace__ = "urn:ControllerService"
	
	requestId = String.customize(min_occurs=1, max_occurs=1, nillable=False, namespace="urn:CommonTypes")
	status = Status.customize(min_occurs=1, max_occurs='unbounded', nillable=True)

class ReceiveStatus(ComplexModel):
	__namespace__ = "urn:ControllerService"

	status = RequestStatus.customize(max_occurs="unbounded", nillable=False)

class Message(ComplexModel):
	__namespace__ = "urn:CommonTypes"

	sourceNodeId = String.customize(nillable=False, min_occurs=1)
	timestamp = DateTime.customize(nillable=False, min_occurs=1)
	binaryData = ByteArray.customize(nillable=False, min_occurs=1)

class ControllerService(ServiceBase):

	@srpc()
	def experimentEnded():
		print ":: ControllerService -> experimentEnded"

	@srpc(Message.customize(min_occurs=1, max_occurs='unbounded', nillable=False))
	def receive(msg):
		print ":: ControllerService -> receive [%s]" % msg
		for m in msg:
			nodeid = m.sourceNodeId.split(':')[-1]
			try:
				node = models.Node.query.filter(models.Node.resource_id == nodeid).one()
			except NoResultFound:
				print ":: ControllerService -> receive: data from an unknown node '%s'" % m.sourceNodeId
			try:
				# TODO check also for node
				job = models.Job.query.filter(models.Job.datetime_from < times.now()).\
									   filter(models.Job.datetime_to > times.now()).\
									   one()
			except NoResultFound:
				print ":: ControllerService -> receive: can't find corresponding job"
				return
			except MultipleResultsFound:
				print ":: ControllerService -> receive: multiple matching jobs found"
				return
			try:
				trace = models.Trace.query.filter(models.Trace.job == job).one()
			except NoResultFound:
				# we're the first
				trace = models.Trace('wisebed trace')
				trace.job = job
				db_session.add(trace)
			except MultipleResultsFound:
				print ":: ControllerService -> receive: multiple matching traces found"
				return
			t = models.TraceEntry("%s:%s: %s" % (m.timestamp, nodeid, m.binaryData))
			trace.content.append(t)
		db_session.commit()

	@srpc(String.customize(min_occurs=1, max_occurs='unbounded', nillable=False))
	def receiveNotification(msg):
		print ":: ControllerService -> receiveNotification [%s]" % msg

	@srpc(RequestStatus.customize(min_occurs=1, max_occurs='unbounded', nillable=False))
	def receiveStatus(status):
		print ":: ControllerService -> receiveStatus [%s]" % status
		for rqs in status:
			try:
				s = models.Status.query.filter(models.Status.resource_id == rqs.requestId).one()
				for sts in rqs.status:
					s.message = sts.msg
					s.num_done = sts.value
				db_session.commit()
			except NoResultFound:
				print ":: ControllerService -> receiveStatus: no matching requestId in database"

if __name__ == '__main__':
	try:
		from wsgiref.simple_server import make_server
	except ImportError:
		print "Error: spyne server code requires Python >= 2.5"

	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

	application = Application([ControllerService], 'urn:ControllerService',
			interface=Wsdl11(), in_protocol=Soap11(), out_protocol=Soap11())

	server = make_server('0.0.0.0', 7789, WsgiApplication(application))

	print "listening to http://0.0.0.0:7789"
	print "wsdl is at: http://localhost:7789/?wsdl"

	server.serve_forever()
