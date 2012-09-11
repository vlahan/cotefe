#
# views.py
#  SQLAlchemy model of the CONET resource model.
#  
# Created by Martin Bor <m.c.bor@tudelft.nl> on 2012-09-10
# Copyright (c) 2012 TU Delft. All rights reserved.
#

# TODO
# * return more verbose json errors
# * move views/registration URLs to separate files?

import os
try:
	from collections import OrderedDict as odict
except ImportError:
	from odict import odict

import times

from flask import url_for, abort, json, send_from_directory, request, make_response, jsonify
from flask.views import MethodView

from bottlerocket import app
from bottlerocket.database import db_session
from bottlerocket.proxy import wisebed_proxy
from bottlerocket.models import Testbed, Node, Job, Platform, Radio, ImageFormat, User, Image, Resource, Status, NodeGroup, Trace

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

def register_api(view, endpoint, url, pk='id', pk_type='int'):
	view_func = view.as_view(endpoint)
	app.add_url_rule(url, defaults={pk: None},
			view_func=view_func, methods=['GET',])
	app.add_url_rule(url, view_func=view_func, methods=['POST'])
	app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
			methods=['GET', 'PUT', 'PATCH', 'DELETE'])

def to_json(resp, mimetype='application/json'):
	response = make_response(json.dumps(resp, indent=4))
	response.headers['Content-Type'] = mimetype
	return response

def api_url(endpoint, **kwargs):
	return url_for(endpoint, _external=True, _method='GET', **kwargs)

@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path,'static'), 
			'favicon.ico',
			mimetype='image/vnd.microsoft.icon')

def json_error(code, message):
	return jsonify(status=code, message=message), code

@app.errorhandler(404)
def resource_not_found(error):
	return jsonify(status=error.code, message='resource not found'), 404

@app.errorhandler(400)
def bad_request(error):
	return jsonify(status=error.code, message='invalid resource'), 400
	
class ResourceView(MethodView):
	def get(self, *args, **kwargs):
		abort(405)

	def post(self, *args, **kwargs):
		abort(405)

class TestbedAPI(ResourceView):
	def get(self, id):
		# ignore the id, and pick the first Testbed we find
		testbed = Testbed.query.first()
		if testbed == None:
			app.logger.warning("can't find a testbed")
			abort(404)
		resp = odict()
		# XXX testbed is special
		if testbed.uri is None:
			resp['uri'] = api_url('testbed')
		else:
			resp['uri'] = testbed.uri
		resp['media_type'] = testbed.media_type
		resp['name'] = testbed.name
		resp['organization'] = testbed.organization
		# TODO sockets
		if testbed.nodes:
			resp['nodes'] = testbed.nodes
		else:
			resp['nodes'] = api_url('node')
		resp['nodegroups'] = api_url('nodegroup')
		if testbed.platforms:
			resp['platforms'] = testbed.platforms
		else:
			resp['platforms'] = api_url('platform')
		# TODO sensors
		# TODO actuators
		# TODO interfaces
		if testbed.jobs:
			resp['jobs'] = testbed.jobs
		else:
			resp['jobs'] = api_url('job')
		resp['status'] = api_url('status')
		resp['traces'] = api_url('trace')
		return to_json(resp)

class NodeAPI(ResourceView):
	def get(self, id):
		if id is None:
			q = Node.query
			if 'platform' in request.args:
				platform = request.args['platform']
				q = q.join(Node.platform).filter(Platform.resource_id == platform)
			if 'n' in request.args:
				try:
					n = int(request.args['n'])
				except ValueError:
					abort(400)
				q = q.limit(n)
			nodes = q.all()
			resp = [Resource.to_dict(node) for node in nodes]
			return to_json(resp)
		else:
			try:
				node = Node.query.filter(Node.resource_id == id).one()
			except NoResultFound:
				abort(404)
			resp = node.to_dict()
			return to_json(resp) 

	def put(self, id):
		try:
			node = Node.query.filter(Node.resource_id == id).one()
		except NoResultFound:
			abort(404)
		try:
			new_node = json.loads(request.data)
		except ValueError:
			abort(400)
		# XXX only handles uploading new images
		# TODO support other updates
		try:
			# get the image binary
			image_id = new_node['image']['uri'].split('/')[-1]
			try:
				image = Image.query.filter(Image.id == image_id).one()
			except NoResultFound:
				app.logger.warning("image %s is not a local image" % new_node)
				abort(400)
			try:
				# find the current job
				job = Job.query.filter(Job.nodes.contains(node)).\
								filter(Job.datetime_from < times.now()).\
								filter(Job.datetime_to > times.now()).\
								one()
			except NoResultFound:
				app.logger.warning("can't find reservation")
				return jsonify(error="no reservation found for the specified node, can't flash node."),409
			except MultipleResultsFound:
				app.logger.warning("found multiple reservations")
				return jsonify(error="multiple reservations found, can't flash node."), 500

			# flash the node
			request_id = wisebed_proxy.flash_node(job.reservation_key, node.resource_id, image.content)

			# create a new status resource for tracking progress
			status = Status(request_id)
			status.resource_id = request_id
			status.num_done = 0
			status.num_tot = 100
			status.target = request.url
			db_session.add(status)

			# update the node representation
			node.image = image

			db_session.commit()
			return to_json(status.to_dict()), 202
		except KeyError, e:
			app.logger.warning("node put keyerror:", e)

class JobAPI(ResourceView):
	def get(self, id):
		if id is None:
			jobs = Job.query.filter(Job.datetime_from >= times.now()).all()
			resp = [Resource.to_dict(job) for job in jobs]
			return to_json(resp)
		else:
			try:
				job = Job.query.filter(Job.id == id).one()
			except NoResultFound:
				abort(404)
			resp = job.to_dict()
			return to_json(resp)

	def post(self):
		if request.json is None:
			abort(400)
		try:
			datetime_from = times.to_universal(request.json['datetime_from'])
			datetime_to = times.to_universal(request.json['datetime_to'])
		except ValueError, e:
			return jsonify(error="can't convert datetime: " + e.message), 400
		# TODO check datetime_to - datetime_from > 0
		# create Job resource
		reservation = Job(request.json['name'])
		reservation.description = request.json['description']
		reservation.datetime_from = datetime_from
		reservation.datetime_to = datetime_to
		for node in request.json['nodes']:
			try:
				n = Node.query.filter(Node.resource_id == node).one()
			except NoResultFound:
				abort(400)
			reservation.nodes.append(n)
		# make the reservation
		try:
			reservation_key = wisebed_proxy.create_job(datetime_from, datetime_to, request.json['nodes'])
		except Exception, e:
			return jsonify(error=str(e)), 500
		reservation.reservation_key = reservation_key
		db_session.add(reservation)
		db_session.commit()
		return (to_json(reservation.to_dict()), 201, {'Location': api_url('job', id=reservation.id)})

	def put(self, id):
		try:
			job = Job.query.filter(Job.id == id).one()
		except NoResultFound:
			abort(404)
		try:
			new_job = json.loads(request.data)
		except ValueError:
			abort(400)
		try:
			datetime_from = times.to_universal(new_job['datetime_from'])
			datetime_to = times.to_universal(new_job['datetime_to'])
		except ValueError, e:
			return jsonify(error="Can't convert datetime: " + e.message), 400

		job.name = new_job['name']
		job.description = new_job['description']
		job.datetime_from = datetime_from
		job.datetime_to = datetime_to
		job.nodes = []
		# TODO only query / change the proxy when the nodes and/or datetime has changed
		for node in new_job['nodes']:
			try:
				n = Node.query.filter(Node.resource_id == node).one()
			except NoResultFound:
				abort(400)
			job.nodes.append(n)
		try:
			wisebed_proxy.delete_job(job.reservation_key)
			reservation_key = wisebed_proxy.create_job(datetime_from, datetime_to, new_job['nodes'])
		except Exception, e:
			return jsonify(error=str(e)), 500
		job.reservation_key = reservation_key
		db_session.commit()
		return to_json(job.to_dict()), 200

	def delete(self, id):
		try:
			job = Job.query.filter(Job.id == id).one()
		except NoResultFound:
			abort(404)
		try:
			wisebed_proxy.delete_job(job.reservation_key)
		except Exception, e:
			return jsonify(error=str(e)), 500
		db_session.delete(job)
		db_session.commit()
		return 'OK', 200

class UserAPI(ResourceView):
	def get(self, id):
		if id:
			try:
				user = User.query.filter(User.id == id).one()
			except NoResultFound:
				abort(404)
			resp = user.to_dict()
			return to_json(resp)
		else:
			users = User.query.all()
			resp = [Resource.to_dict(user) for user in users]
			return to_json(resp)

class ImageFormatAPI(ResourceView):
	def get(self, id):
		if id:
			try:
				imageformat = ImageFormat.query.filter(ImageFormat.resource_id  == id).one()
			except NoResultFound:
				abort(404)
			resp = imageformat.to_dict()
			return to_json(resp)
		else:
			imageformats = ImageFormat.query.all()
			resp = [Resource.to_dict(imageformat) for imageformat in imageformats]
			return to_json(resp)
	
class PlatformAPI(ResourceView):
	def get(self, id):
		if id:
			platform = Platform.query.filter(Platform.resource_id == id).first()
			if platform is None:
				abort(404)
			resp = platform.to_dict()
			return to_json(resp)
		else:
			platforms = Platform.query.all()
			resp = [Resource.to_dict(platform) for platform in platforms]
			return to_json(resp)

class RadioAPI(ResourceView):
	def get(self, id):
		if id:
			try:
				radio = Radio.query.filter(Radio.resource_id == id).one()
			except NoResultFound:
				abort(404)
			resp = radio.to_dict()
			return to_json(resp)
		else:
			radios = Radio.query.all()
			resp = [Resource.to_dict(radio) for radio in radios]
			return to_json(resp)

class ImageAPI(ResourceView):
	def get(self, id):
		if id:
			try:
				image = Image.query.filter(Image.id == id).one()
			except NoResultFound:
				abort(404)
			resp = image.to_dict()
			return to_json(resp)
		else:
			images = Image.query.all()
			resp = [Resource.to_dict(image) for image in images]
			return to_json(resp)

	def post(self):
		if request.json is None:
			abort(400)
		image = Image(request.json['name'])
		image.description = request.json['description']
		# TODO owner
		# TODO image format
		db_session.add(image)
		db_session.commit()
		return to_json(image.to_dict()), 200, {'Location' : api_url('image', id=image.id)}

	def put(self, id):
		# TODO change image
		return "change image"

	def delete(self, id):
		try:
			image = Image.query.filter(Image.id == id).one()
		except NoResultFound:
			abort(404)
		db_session.delete(image)
		db_session.commit()
		return 'OK', 200

class ImageFileAPI(ResourceView):
	def get(self, id):
		if id:
			try:
				image = Image.query.filter(Image.id == id).one()
			except NoResultFound:
				abort(404)
			if image.content is None:
				return '', 204
			resp = make_response(image.content)
			resp.headers['Content-Type'] = 'application/octet-stream'
			resp.headers['Content-Disposition'] = 'attachment; filename=%s' % image.name
			return resp
		else:
			abort(404)

	def post(self, id):
		if id:
			image = Image.query.filter(Image.id == id).one()
			image.content = request.files['imagefile'].stream.getvalue()
			db_session.commit()
			return 'OK', 201
		else:
			abort(400)

class NodeGroupAPI(ResourceView):
	def get(self, id):
		if id:
			try:
				nodegroup = NodeGroup.query.filter(NodeGroup.id == id).one()
			except NoResultFound:
				abort(404)
			resp = nodegroup.to_dict()
			return to_json(resp)
		else:
			nodegroups = NodeGroup.query.all()
			resp = [Resource.to_dict(nodegroup) for nodegroup in nodegroups]
			return to_json(resp)

	def post(self):
		if request.json is None:
			abort(400)
		nodegroup = NodeGroup(request.json['name'])
		for node in request.json['nodes']:
			try:
				n = Node.query.filter(Node.resource_id == node).one()
			except NoResultFound:
				return jsonify(error="node %s doesn't exist" % node), 400
			nodegroup.nodes.append(n)
		db_session.add(nodegroup)
		db_session.commit()
		return to_json(nodegroup.to_dict()), 201, {'Location': api_url('nodegroup', id=nodegroup.id)}

	def put(self, id):
		if id:
			if request.json is None:
				abort(400)
			try:
				nodegroup = NodeGroup.query.filter(NodeGroup.id == id).one()
			except NoResultFound:
				abort(404)
			if request.json.has_key(['name']):
				nodegroup.name = request.json['name']
			if request.json.has_key(['nodes']):
				nodegroup.nodes = []
				for node in request.json['nodes']:
					try:
						n = Node.query.filter(Node.resource_id == node).one()
					except NoResultFound:
						return jsonify(error="node %s doesn't exist" % node), 400
					nodegroup.nodes.append(n)
			db_session.commit()
			return to_json(nodegroup.to_dict()), 200
		else:
			abort(400)

class NodeGroupImageAPI(ResourceView):
	def put(self, id, image_id):
		if id and image_id:
			try:
				nodegroup = NodeGroup.query.filter(NodeGroup.id == id).one()
			except NoResultFound:
				abort(404)
			try:
				image = Image.query.filter(Image.id == image_id).one()
			except NoResultFound:
				abort(404)
			try:
				# TODO check if we also reserved the required nodes
				job = Job.query.filter(Job.datetime_from < times.now()).\
								filter(Job.datetime_to > times.now()).\
								one()
			except NoResultFound:
				print "can't find reservation"
				return json_error(409, "can't find reservation for specified nodes")
				#abort(409)
			except MultipleResultsFound:
				print "multiple reservations found"
				abort(500)

			# flash the nodes
			request_id = wisebed_proxy.flash_nodes(job.reservation_key, [node.resource_id for node in nodegroup.nodes], image.content)

			# create a new status resource for tracking progress
			status = Status(request_id)
			status.resource_id = request_id
			status.num_done = 0
			status.num_tot = 100
			status.target = request.url
			db_session.add(status)

			# update the node representations
			for node in nodegroup.nodes:
				node.image = image

			db_session.commit()
			return to_json(status.to_dict()), 202
		else:
			abort(400)


class StatusAPI(ResourceView):
	def get(self, id):
		if id:
			try:
				status = Status.query.filter(Status.resource_id == id).one()
			except NoResultFound:
				abort(404)
			resp = status.to_dict()
			return to_json(resp)
		else:
			statuses = Status.query.all()
			resp = [Resource.to_dict(status) for status in statuses]
			return to_json(resp)

class TraceAPI(ResourceView):
	def get(self, id):
		if id:
			try:
				trace = Trace.query.filter(Trace.id == id).one()
			except NoResultFound:
				abort(404)
			resp = trace.to_dict()
			return to_json(resp)
		else:
			traces = Trace.query.all()
			resp = [Resource.to_dict(trace) for trace in traces]
			return to_json(resp)

register_api(TestbedAPI, 'testbed', '/')
register_api(NodeAPI, 'node', '/nodes/', pk_type='string')
register_api(JobAPI, 'job', '/jobs/')
register_api(PlatformAPI, 'platform', '/platforms/', pk_type='string')
register_api(RadioAPI, 'radio', '/radios/', pk_type='string')
register_api(ImageFormatAPI, 'imageformat', '/imageformats/', pk_type='string')
register_api(ImageAPI, 'image', '/images/')
app.add_url_rule('/images/<int:id>/upload', view_func=ImageFileAPI.as_view('image_file'), methods=['POST'])
app.add_url_rule('/images/<int:id>/download', view_func=ImageFileAPI.as_view('image_file'), methods=['GET'])
register_api(NodeGroupAPI, 'nodegroup', '/nodegroups/')
app.add_url_rule('/nodegroups/<int:id>/image/<int:image_id>', view_func=NodeGroupImageAPI.as_view('nodegroup_image'), methods=['PUT'])
register_api(StatusAPI, 'status', '/status/', pk_type='string')
register_api(TraceAPI, 'trace', '/traces/')
