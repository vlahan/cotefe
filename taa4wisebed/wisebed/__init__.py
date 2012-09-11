#
# __init__.py
#  Wisebed client.
#
# Created by Martin Bor <m.c.bor@tudelft.nl> on 2012-09-10
# Copyright (c) 2012 TU Delft. All rights reserved.
#

from suds import WebFault
from suds.client import Client
import os
import base64
import config

BASE = os.path.abspath(os.path.dirname(__file__))

# TODO suds logging to file (ie)
class AuthenticationExcepton(Exception):
	pass

class ReservationException(Exception):
	DESCRIPTIONS = {
			'soap:203': 'The reservation key is not known',
			'soap:202': 'The user is not known',
			'soap:201': 'The user is not authorized to do this',
			'soap:102': 'Some nodes are not known',
			'soap:101': 'Some nodes are already reserved',
			'soap:301': 'Trouble accessing the database',
			'soap:401': 'Can not delete the reservation of a running experiment',
	}

	def __init__(self, fault):
		self.message = self.DESCRIPTIONS[fault]

	def __str__(self):
		return repr(self.message)


class Wisebed(object):

	def __init__(self):
		self.__rs = Client("file://" + BASE + "/wsdl/RS.wsdl")
		self.__snaa = Client("file://" + BASE + "/wsdl/SNAA.wsdl")
		self.__sma = Client("file://" + BASE + "/wsdl/SessionManagementService.wsdl")
		self.__wsn = Client("file://" + BASE + "/wsdl/WSNService.wsdl")

		self.secret = self.authenticate(config.WISEBED_USERNAME, config.WISEBED_PASSWORD, config.WISEBED_URN_PREFIX)
		self.__secret = self.secret

	def authenticate(self, username, password, urn_prefix):
		# TODO handle errors/exceptions
		auth_data = self.__snaa.factory.create('authenticationTriple')
		auth_data.username = username 
		auth_data.password = password 
		auth_data.urnPrefix = urn_prefix
		try:
			return self.__snaa.service.authenticate(auth_data)
		except WebFault, e:
			raise AuthenticationExcepton(e)
		
	def create_job(self, datetime_from, datetime_to, nodes):
		reservation = self.__rs.factory.create('confidentialReservationData')
		reservation['from'] = datetime_from
		reservation['to'] = datetime_to
		# TODO refactor URN prefix
		reservation['nodeURNs'] = ['urn:wisebed:node:tud:' + node for node in nodes]
		reservation['userData'] = 'reserved'
		try:
			reservation_key = self.__rs.service.makeReservation(self.__secret, reservation)
			return reservation_key[0][0]
		except WebFault, e:
			raise ReservationException(e.fault.faultcode)
							
	def delete_job(self, key):
		srk = self.__rs.factory.create('secretReservationKey')
		srk['secretReservationKey'] = key
		srk['urnPrefix'] = config.WISEBED_URN_PREFIX
		try:
			self.__rs.service.deleteReservation(self.secret, srk)
		except WebFault, e:
			raise ReservationException(e.fault.faultcode)

	def flash_node(self, key, node, image):
		return self.flash_nodes(key, [node], image)

	def flash_nodes(self, key, nodes, image):
		# TODO cache instance URL
		srk = self.__rs.factory.create('secretReservationKey')
		srk['secretReservationKey'] = key
		srk['urnPrefix'] = config.WISEBED_URN_PREFIX
		instance_url = self.__sma.service.getInstance(srk, config.WISEBED_CTRL_ENDPOINT)
		self.__wsn.set_options(location=instance_url)
		program = self.__wsn.factory.create('program')
		program['program'] = base64.b64encode(image)
		request_id = self.__wsn.service.flashPrograms(['urn:wisebed:node:tud:' + node for node in nodes], [0]*len(nodes), [program])
		return request_id

