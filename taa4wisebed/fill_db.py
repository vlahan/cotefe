#!/usr/bin/env python
#
# fill_db.py
#  Initialize and fill the database with information 
#  from the Rack testbed @ TU Delft.
#
# Created by Martin Bor <m.c.bor@tudelft.nl> on 2012-09-10
# Copyright (c) 2012 TU Delft. All rights reserved.
#

from bottlerocket.database import init_db, db_session as db
from bottlerocket.models import *
from lxml import etree
from suds.client import Client
from cStringIO import StringIO
import config
import os

BASE = "file://" + os.path.abspath(os.path.dirname(__file__)) + "/wisebed/wsdl/"

rs = Client(BASE + "RS.wsdl")
snaa = Client(BASE + "SNAA.wsdl")
sma = Client(BASE + "SessionManagementService.wsdl")

ns = '{http://wisebed.eu/ns/wiseml/1.0}'
urn_prefix = 'urn:wisebed:node:tud:'

def authenticate():
	auth_data = snaa.factory.create('authenticationTriple')
	auth_data.username = config.WISEBED_USERNAME
	auth_data.password = config.WISEBED_PASSWORD
	auth_data.urnPrefix = config.WISEBED_URN_PREFIX
	return snaa.service.authenticate(auth_data)

print "init db"
init_db()

print "testbed"
testbed = Testbed('the Rack')
testbed.organization = 'TU Delft'
db.add(testbed)

print "image formats"

elf = ImageFormat('ELF')
elf.resource_id = "elf"
srec = ImageFormat('SREC')
srec.resource_id = "srec"
ihex = ImageFormat('IHEX')
ihex.resource_id = "ihex"

db.add_all([elf, srec, ihex])

print "platforms"
gnode = Platform('GNode')
gnode.uri = 'https://api.cotefe.net/platforms/gnode'
gnode.resource_id = "gnode"
gnode.cpu = 'TI MSP430F2418'
gnode.memory = '116'
gnode.image_formats = [ elf, ihex ]
gnode.bandwidth_lower_bound = 300
gnode.bandwidth_upper_bound = 928

tnode = Platform('TNOde')
tnode.uri = 'https://api.cotefe.net/platforms/tnode'
tnode.resource_id = "tnode"
tnode.cpu = 'Atmel ATmega128L'
tnode.memory = '128'
tnode.image_formats = [ elf, srec ]
tnode.bandwidth_lower_bound = 300
tnode.bandwidth_upper_bound = 1000

tmote = Platform('TMote Sky')
tmote.resource_id = "tmotesky"
tmote.uri = "https://api.cotefe.net/platforms/tmotesky"
tmote.cpu = 'TI MSP430F1611'
tmote.memory = '48'
tmote.image_formats = [ elf, ihex ]
tmote.bandwidth_lower_bound = 2400
tmote.bandwidth_upper_bound = 2483.5

db.add_all([gnode, tnode, tmote])

print "radios"

cc1101 = Radio('CC1101')
cc1101.resource_id = "cc1101"
cc1000 = Radio('CC1000')
cc1000.resource_id = "cc1000"
cc2420 = Radio('CC2420')
cc2420.resource_id = "cc2420"

db.add_all([cc1101, cc1000, cc2420])

print "mobility"
static_mobility = Mobility('static')
static_mobility.resource_id = "static"
static_mobility.description = 'Static node mobility'

db.add(static_mobility)

print "nodes"

wiseml = etree.parse(StringIO(sma.service.getNetwork()))
for e in wiseml.iter(ns + 'node'):
	# TODO handle default node
	node_id = e.get('id')
	if node_id is None:
		continue
	node_name = node_id.replace(urn_prefix,'')
	node = Node(node_name)
	node.resource_id = node.name
	position = e.find(ns + 'position')
	node.x_coord = float(position.find(ns + 'x').text)
	node.y_coord = float(position.find(ns + 'y').text)
	node.z_coord = float(position.find(ns + 'z').text)
	platform = e.find(ns + 'nodeType').text
	if platform == 'GNode':
		node.platform = gnode
		node.radio = [ cc1101 ]
	elif platform == 'TNOde':
		node.platform = tnode
		node.radio = [ cc1000 ]
	elif platform == 'TMoteSky':
		node.platform = tmote
		node.radio = [ cc2420 ]
	else:
		print 'Unknown platform "%s"' % platform
	node.power = True
	node.mobility = static_mobility
	# TODO sensors
	db.add(node)
db.flush()

print "image"

blink_tmote = Image('blink.tmote')
blink_tmote.description = "blink leds for Tmote Sky"
blink_tmote.imageformat = elf
blink_tmote.content = open('images/blink.tmote', 'r').read()

blink_gnode = Image('blink.gnode')
blink_gnode.description = "blink leds for Gnode"
blink_gnode.imageformat = elf
blink_gnode.content = open('images/blink.gnode', 'r').read()

hello_gnode = Image('hello.gnode')
hello_gnode.description = "hello world for Gnode"
hello_gnode.imageformat = elf
hello_gnode.content = open('images/hello.gnode', 'r').read()

db.add_all([blink_tmote, blink_gnode, hello_gnode])

db.flush()

print "authenticate"
secret = authenticate()

print "jobs"
jobs = rs.service.getReservations('1971-01-01', '2050-01-01')
for job in jobs:
	j = Job('wisebed')
	j.datetime_from = job['from']
	j.datetime_to = job['to']
	j.description = job['userData']
	for node in job['nodeURNs']:
		node = node.replace(urn_prefix,'')
		n = Node.query.filter(Node.name == node).first()
		if n is None:
			print "can't find node " + node
		j.nodes.append(n)
	db.add(j)

print "commit..."
db.commit()

# close session
db.remove()
