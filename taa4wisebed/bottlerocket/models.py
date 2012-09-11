#
# models.py
#  SQLAlchemy model of the CONET resource model.
#  
# Created by Martin Bor <m.c.bor@tudelft.nl> on 2012-09-10
# Copyright (c) 2012 TU Delft. All rights reserved.
#

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Table, LargeBinary, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from bottlerocket.database import Base
from bottlerocket import app
from flask import url_for
try:
	from collections import OrderedDict as odict
except ImportError:
	from odict import odict

# TODO
# * add cascade update/delete rules?
# * cleanup tables / replace Testbed Federation table with uri's
# * cleanup iterator

def junction_table(a, b):
	return Table('%s_%s' % (a,b), Base.metadata,
			Column('%s_id' % a, Integer, ForeignKey('%s.id' % a), primary_key=True),
			Column('%s_id' % b, Integer, ForeignKey('%s.id' % b), primary_key=True)
		)

def api_url(endpoint, **kwargs):
	with app.app_context():
		return url_for(endpoint, _external=True, _method='GET', **kwargs)

class Resource(object):
	id = Column(Integer, primary_key=True)
	resource_id = Column(String, unique=True)
	uri = Column(String)
	name = Column(String)

	@declared_attr
	def __tablename__(cls):
		return cls.__name__.lower()

	@property
	def media_type(self):
		# XXX for future use:
		# return 'application/ctf.' + self.__class__.__name__ + '+json'
		return 'application/json'

	def __init__(self, name):
		self.name = name

	def __iter__(self):
		return self.next()

	def next(self):
		yield 'media_type', self.media_type
		for column in self.__table__.columns.keys():
			yield column, getattr(self, column)
	
	def to_dict(self):
		r = odict()
		if self.uri is None:
			r['uri'] = api_url(self.__class__.__name__.lower(), id=self.resource_id or self.id)
		else:
			r['uri'] = self.uri
		r['media_type'] = self.media_type
		r['name'] = self.name
		return r

	def __repr__(self):
		return "<%s('%s')>" % (self.__class__.__name__, self.name)

class Platform(Base, Resource):
	cpu = Column(String)
	memory = Column(Integer)
	bandwidth_lower_bound = Column(Integer)
	bandwidth_upper_bound = Column(Integer)

	imageformats = relationship('ImageFormat', secondary=junction_table('platform', 'imageformat'))
	
	def __init__(self, name):
		self.name = name
	
	def to_dict(self):
		r = Resource.to_dict(self)
		r['memory'] = self.memory
		r['bandwidth_lower_bound'] = self.bandwidth_lower_bound
		r['bandwidth_upper_bound'] = self.bandwidth_upper_bound
		r['image_formats'] = [Resource.to_dict(imageformat) for imageformat in self.imageformats]
		return r
	
class ImageFormat(Base, Resource):
	def __init__(self, name):
		self.name = name

class Node(Base, Resource):
	platform_id = Column(Integer, ForeignKey('platform.id'))
	platform  = relationship('Platform')

	interfaces = relationship('Interface', secondary=junction_table('node', 'interface'))

	# TODO sensors
	# TODO actuators
	radio = relationship('Radio', secondary=junction_table('node', 'radio'))

	mobility_id = Column(Integer, ForeignKey('mobility.id'))
	mobility = relationship('Mobility')

	power = Column(Boolean)

	image_id = Column(Integer, ForeignKey('image.id'))
	image = relationship('Image')

	x_coord = Column(Float)
	y_coord = Column(Float)
	z_coord = Column(Float)

	def __init__(self, name):
		self.name = name

	def to_dict(self):
		r = Resource.to_dict(self)
		r['platform'] = Resource.to_dict(self.platform)
		# TODO interfaces
		# TODO sensors
		# TODO actuators
		# TODO mobility
		r['radio'] = [Resource.to_dict(radio) for radio in self.radio]
		r['power'] = self.power
		if self.image is None:
			r['image'] = None
		else:
			r['image'] = Resource.to_dict(self.image)
		r['x_coord'] = self.x_coord
		r['y_coord'] = self.y_coord
		r['z_coord'] = self.z_coord
		return r

class NodeGroup(Base, Resource):
	nodes = relationship('Node', secondary=junction_table('nodegroup', 'node'))

	def __init__(self, name):
		self.name = name

	def to_dict(self):
		r = Resource.to_dict(self)
		r['nodes'] = [Resource.to_dict(node) for node in self.nodes]
		return r

class Interface(Base, Resource):
	def __init__(self, name):
		self.name = name

class Radio(Base, Resource):
	def __init__(self, name):
		self.name = name

class Mobility(Base, Resource):
	description = Column(String)

	def __init__(self, name):
		self.name = name

	def to_dict(self):
		r = Resource.to_dict(self)
		r['description'] = self.description
		return r

class Image(Base, Resource):
	description = Column(String)

	owner_id = Column(Integer, ForeignKey('user.id'))
	owner = relationship('User')
	
	imageformat_id = Column(Integer, ForeignKey('imageformat.id'))
	imageformat = relationship('ImageFormat')
	
	content = Column(LargeBinary)
	# TODO mapping_keys
	# TODO mapping_values

	def __init__(self, name):
		self.name = name

	def to_dict(self):
		r = Resource.to_dict(self)
		r['description'] = self.description
		if self.owner is not None:
			r['owner'] = Resource.to_dict(self.owner)
		if self.imageformat is not None:
			r['image_format'] = Resource.to_dict(self.imageformat)
		r['upload'] = url_for('image_file', _external=True, _method='POST', id=self.id)
		if self.content is not None:
			r['download'] = url_for('image_file', _external=True, _method='GET', id=self.id)
		return r

class User(Base, Resource):
	openid = Column(String)
	email = Column(String)
	organization = Column(String)
	
	projects = relationship('Project', secondary=junction_table('user', 'project'), backref="user")
	experiments = relationship("Experiment", backref="owner")
	jobs = relationship("Job", backref="owner")

	def __init__(self, name):
		self.name = name

	def to_dict(self):
		r = Resource.to_dict(self)
		r['openid'] = self.openid
		r['email'] = self.email
		r['organization'] = self.organization
		r['projects'] = [Resource.to_dict(project) for project in self.projects]
		r['experiments'] = [Resource.to_dict(experiment) for experiment in self.experiments]
		r['jobs'] = [Resource.to_dict(job) for job in self.jobs]
		return r

class Job(Base, Resource):
	description = Column(String)
	owner_id = Column(Integer, ForeignKey('user.id'))
	project_id = Column(Integer, ForeignKey('project.id'))
	experiment_id = Column(Integer, ForeignKey('experiment.id'))
	# TODO testbed
	# TODO platform
	datetime_from = Column(DateTime)
	datetime_to = Column(DateTime)

	# secretReservationKey from WISEBED
	reservation_key = Column(String)

	@property
	def duration(self):
		if self.datetime_to and self.datetime_from:
			delta = self.datetime_to - self.datetime_from
			# return timedelta in minutes
			return int(round(delta.total_seconds() / 60))
		else:
			return None

	nodes = relationship('Node', secondary=junction_table('job', 'node'))
	nodegroups = relationship('NodeGroup', secondary=junction_table('job', 'nodegroup'))
	# TODO tasks[]
	# TODO traces[]

	def __init__(self, name):
		self.name = name

	def to_dict(self):
		r = Resource.to_dict(self)
		r['description'] = self.description
		# TODO owner
		# TODO project
		# TODO experiment
		# TODO testbed
		# TODO platform
		r['datetime_from'] = self.datetime_from.isoformat()
		r['datetime_to'] = self.datetime_to.isoformat()
		r['duration'] = self.duration
		r['nodes'] = [Resource.to_dict(node) for node in self.nodes]
		r['node_groups'] = [ Resource.to_dict(nodegroup) for nodegroup in self.nodegroups]
		# TODO tasks
		# TODO traces
		return r

class Project(Base, Resource):
	description = Column(String)
	# TODO users
	testbeds = relationship('Testbed', secondary=junction_table('project', 'testbed'))
	experiments = relationship('Experiment', backref='project')
	jobs = relationship("Job", backref="project")

	def __init__(self, name):
		self.name = name

	def to_dict(self):
		r = Resource.to_dict(self)
		r['testbeds'] = [Resource.to_dict(testbed) for testbed in self.testbeds]
		r['experiments'] = [Resource.to_dict(experiment) for experiment in self.experiments] 
		r['jobs'] = [Resource.to_dict(job) for job in self.jobs]
		return r

class Experiment(Base, Resource):
	description = Column(String)
	owner_id = Column(Integer, ForeignKey('user.id'))
	project_id = Column(Integer, ForeignKey('project.id'))
	testbeds = relationship('Testbed', secondary=junction_table('experiment', 'testbed'))
	image_files = relationship('Image', secondary=junction_table('experiment', 'image'))
	# TODO property_sets
	# TODO virtual_tasks
	# TODO virtual_node_groups
	# TODO virtual_nodes
	jobs = relationship('Job', backref='experiment')
	# TODO traces
	sharing = Column(Enum('public', 'protected', 'private'))

	def __init__(self, name):
		self.name = name

	def to_dict(self):
		r = Resource.to_dict(self)
		r['description'] = self.description
		r['owner'] = Resource.to_dict(self.owner)
		r['project'] = Resource.to_dict(self.project)
		r['testbeds'] = [Resource.to_dict(testbed) for testbed in self.testbeds]
		r['image_files'] = [Resource.to_dict(image_file) for image_file in self.image_files]
		# TODO property_sets
		# TODO virtual_tasks
		# TODO virtual_node_groups
		# TODO virtual_nodes
		r['jobs'] = [Resource.to_dict(job) for job in self.jobs]
		# TODO traces
		r['sharing'] = self.sharing
		return r

class Testbed(Base, Resource):
	organization = Column(String)
	sockets = Column(String)
	nodes = Column(String)
	platforms = Column(String)
	sensors = Column(String)
	actuators = Column(String)
	interfaces = Column(String)
	jobs  = Column(String)

	def __init__(self, name):
		self.name = name

	def to_dict(self):
		r = Resource.to_dict(self)
		r['organization'] = self.organization
		r['sockets'] = self.sockets
		r['nodes'] = self.nodes
		r['platforms'] = self.platforms
		r['sensors'] = self.sensors
		r['actuators'] = self.actuators
		r['interfaces'] = self.interfaces
		r['jobs'] = self.jobs
		return r

class Status(Base, Resource):
	num_done = Column(Integer)
	num_tot = Column(Integer)
	target = Column(String)
	message = Column(String)

	def __init__(self, name):
		self.name = name

	def to_dict(self):
		r = Resource.to_dict(self)
		r['num_done'] = self.num_done
		r['num_tot'] = self.num_tot
		r['target'] = self.target
		r['message'] = self.message
		return r

class Trace(Base, Resource):
	description = Column(String)
	
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship('User')

	project_id = Column(Integer, ForeignKey('project.id'))
	project = relationship('Project')

	experiment_id = Column(Integer, ForeignKey('experiment.id'))
	experiment = relationship('Experiment')

	testbed_id = Column(Integer, ForeignKey('testbed.id'))
	testbed = relationship('Testbed')

	job_id = Column(Integer, ForeignKey('job.id'))
	job = relationship('Job')

	content = relationship('TraceEntry', secondary=junction_table('trace', 'traceentry'))

	def __init__(self, name):
		self.name = name
		self.content = []

	def to_dict(self):
		r = Resource.to_dict(self)
		# TODO user
		# TODO project
		# TODO experiment
		# TODO testbed
		if self.job is not None:
			r['job'] = Resource.to_dict(self.job)
		r['content'] = [str(c) for c in self.content]
		return r

class TraceEntry(Base):
	__tablename__ = 'traceentry'
	id = Column(Integer, primary_key=True)
	entry = Column(String)

	def __init__(self, entry):
		self.entry = entry

	def __repr__(self):
		return self.entry

