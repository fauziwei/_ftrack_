# coding: utf-8
'''Fauzi, fauzi@soovii.com'''

import os
import cv2
import sys
import json
import logging
import argparse
import ftrack_api
import ftrack_api.entity.location
import ftrack_api.event.base
import config
import global_session
import async
import log_setting

basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(basedir)

ftrack_api.symbol.SERVER_LOCATION_ID

class Publisher:

	def __init__(self):

		self.logger = logging.getLogger(__name__ + '.' + self.__class__.__name__)
		# Shared session
		# self.session = global_session.getSession(shared=True)
		# Private session
		self._session = global_session.getSession(shared=False)

		# Tester task
		self.task_id = 'b6eebae0-e9e7-11e6-8ba0-14187740b71a'
		self.task = self._session.get('Task', self.task_id)

	def destroySession(self, shared):
		global_session.destroySession(shared)

	def commit(self, session):
		try:
			session.commit()
		except:
			session.rollback()

	def getParent(self, entity):
		return entity['parent']

	def getParents(self, session, entity):
		parents = []
		for item in entity['link'][:-1]:
			_ = session.get(item['type'], item['id'])
			parents.append(_)
		return parents

	# @async.asynchronous
	def loadAssetTypes(self):
		asset_types = self._session.query('AssetType').all()
		asset_types = sorted(asset_types, key=lambda asset_type: asset_type['name'])
		return asset_types

	def pickLocation(self, manage_data=False):
		location = None
		locations = self._session.query('Location').all()
		try:
			location = next(
				candidate_location for candidate_location in locations
				if (
					manage_data == False
					or not ftrack_api.mixin(candidate_location, ftrack_api.entity.location.UnmanagedLocationMixin)
				)
			)

		except StopIteration:
			pass

		self.logger.debug('Picked location %s.' % location)
		return location

	def publish(self, task=None, asset=None, asset_type=None,
		asset_name=None, resource_identifier=None):

		component_name = asset_name
		component_resoure_identifier = resource_identifier # is path file upload
		component_location = self.pickLocation(manage_data=False)

		components = []
		components.append({
			'locations': [component_location],
			'name': component_name,
			'file_path': component_resoure_identifier
		})

		version_description = 'Added more leaves.'
		preview_path = ''

		self._publish(
			task=task,
			asset=asset,
			asset_type=asset_type,
			asset_name=asset_name,
			components=components,
			version_description=version_description,
			preview_path=preview_path
		)

	# @async.asynchronous
	def _publish(self, task=None, asset=None, asset_type=None, asset_name=None,
		components=None, version_description=None, preview_path=None):

		try:

			# Create Asset
			if asset is None:

				_asset_type = self._session.query(
					'AssetType where short is %s' % asset_type['short']
				).first()

				asset = self._session.query(
					'Asset where name is "%s" '
					'and type_id is "%s" '
					'and parent.id is "%s"' % (asset_name, _asset_type['id'], task['parent_id'])
				).first()

				if asset is None:
					asset = self._session.create('Asset', {
						'name': asset_name,
						'type': _asset_type,
						'parent': task['parent']
					})

			# Create Version
			status = self._session.query('Status where name is "Not started"').first()
			version = self._session.create('AssetVersion', {
				'asset': asset,
				'status': status,
				'comment': version_description,
				'task': task
			})
			self.commit(self._session)

			# server_location = self._session.query('Location where name is "ftrack.server"').first()
			server_location = self._session.get('Location', ftrack_api.symbol.SERVER_LOCATION_ID)

			# Create Components
			for component in components:

				# # because some of file not correct ftrack format.
				# job = version.encode_media(component.get('file_path'))
				# job_data = json.loads(job['data'])
				# component_id_image, component_id_video = None, None
				# for output in job_data['output']:
				# 	if output['format'] == 'image/jpeg':
				# 		component_id_image = output['component_id']
				# 	elif output['format'] == 'video/mp4':
				# 		component_id_video = output['component_id']

					# self.logger.info(u'Output component - id: {0}, format: {1}'.format(
						# output['component_id'], output['format'])
					# )
				# if component_id_video != None:
				# 	self.enableReviewed(component_id_video, None)

				

				# self.logger.info('component_id: %s' % job_data['output']['component_id'])
				# self.logger.info('format: %s' % job_data['output']['format'])
				# self.logger.info('source_component_id: %s' % job_data['source_component_id'])
				# self.logger.info('keep original component: %s' % job_data['keep_original'])

				# self.logger.info('%s' % job)
				# self.logger.info('%s' % server_location.get_url(job['job_components']))

				# for comp in job['job_components']:
					# comp_url = server_location.get_url(comp)
					# self.logger.info('comp_url: %s' % comp_url)

				# ffmpeg = 'C:/Work/Ftrack/ftrack-client/unit_test/ffmpeg/bin/ffmpeg.exe'
				# ffmpeg -i P6090053.mov -ac 2 -b:v 2000k -c:a aac -c:v libx264 -pix_fmt yuv420p -g 30 -vf scale="trunc((a*oh)/2)*2:720" -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 lalala.mov


				comp = version.create_component(
					component.get('file_path'),
					{'name': 'ftrackreview-mp4'},
					# {'name': component.get('name', None)},
					# location=None
					# location='auto'
					location=server_location
				)

				comp['metadata']['ftr_meta'] = json.dumps({
					'frameIn': 0, 'frameOut': 150, 'frameRate': 24.0
				})
				comp.session.commit()

				# because some of file not correct ftrack format.
				# job = version.encode_media(comp)
				# job_data = json.loads(job['data'])
				# component_id_image, component_id_video = None, None
				# for output in job_data['output']:
				# 	if output['format'] == 'image/jpeg':
				# 		component_id_image = output['component_id']
				# 	elif output['format'] == 'video/mp4':
				# 		component_id_video = output['component_id']

				# if component_id_video != None:
				# 	self.enableReviewed(comp['id'], None)



				# for location in component.get('locations', []):
					# location.add_component(comp, server_location)
			self.commit(self._session)

			# if preview_path:
			# 	self._session.event_hub.publish(
			# 		ftrack_api.event.base.Event(
			# 			'ftrack.connect.publish.make-web-playable',
			# 			data=dict(
			# 				versionId=version['id'],
			# 				path=preview_path
			# 			)
			# 		),
			# 		synchronous=True
			# 	)

			# Create thumbnail for video file.
			# fps = None
			# for component in components:
			# 	file_upload = component.get('file_path')

			# 	if sys.platform == 'win32':
			# 		filename = file_upload.split('\\')[-1]
			# 	else:
			# 		filename = file_upload.split('/')[-1]
			# 	name, ext = os.path.splitext(filename)

			# 	if ext in ['.MOV', '.mov']:
			# 		# http://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames
			# 		# https://www.learnopencv.com/how-to-find-frame-rate-or-frames-per-second-fps-in-opencv-python-cpp/
			# 		# get only 1st frame and read fps.
			# 		vidcap = cv2.VideoCapture(file_upload)
			# 		fps = vidcap.get(cv2.cv.CV_CAP_PROP_FPS) # frame/sec
			# 		success, image = vidcap.read()
			# 		cv2.imwrite('images.jpg', image)
			# 		version.create_thumbnail('images.jpg')
			# 		vidcap.release()

			# 		# add image.jpg inside this version
			# 		component_image = version.create_component(
			# 			path='images.jpg',
			# 			data={'name': 'image'},
			# 			location=server_location
			# 		)
			# 		component_image['metadata']['ftr_meta'] = json.dumps({
			# 			'format': 'image'
			# 		})
			# 		component_image.session.commit()


			# version['is_published'] = True
			# self.commit(self._session)

		except Exception as error:
			self._cleanupFailedPublish(version=version)
			raise

		# self.enableReviewed(comp['id'], fps)


	def _cleanupFailedPublish(self, version=None):
		try:
			if version:
				self._session.delete(version)
				self.commit(self._session)
		except:
			self.logger.exception('Failed to clean up version after failed publish.')


	def enableReviewed(self, component_id=None, fps=None):
		component = self._session.get('FileComponent', component_id)
		version = component['version']

		images = ['.BMP', '.bmp', '.JPEG', '.JPG', '.jpeg', '.jpg', '.GIF', '.gif', '.PNG', '.png', '.TIFF', '.TIF', '.tiff', '.tif']
		videos = ['.MOV', '.mov', '.MP4', '.mp4', '.AVI', '.avi', '.MKV', '.mkv']

		if component['file_type'] in images:
			# Create new review component with required metadata.
			review_component = self._session.create('FileComponent', {
				'name': 'ftrackreview-image',
				'file_type': component['file_type'],
				'version': version
			})
			review_component['metadata'] = {
				'source_component_id': component['id'],
				'ftr_meta': json.dumps({
				'format': 'image'
				})
			}

			# Copy data from source to review component.
			source_location = self._session.pick_location(component)
			server_location = self._session.get('Location', ftrack_api.symbol.SERVER_LOCATION_ID)
			resource_identifier = server_location.structure.get_resource_identifier(review_component)
			server_location._add_data(component, resource_identifier, source_location)

			# Register component in server location
			self._session.create(
				'ComponentLocation', data=dict(
					component=review_component,
					location=server_location,
					resource_identifier=resource_identifier
				)
			)

			# Commit before setting thumbnail to ensure thumbnail has been persisted.
			self.commit(self._session)

			version['thumbnail_id'] = review_component['id']
			self.commit(self._session)


		elif component['file_type'] in videos:
			# Create mp4
			# Create new review component with required metadata.
			review_component = self._session.create('FileComponent', {
				'name': 'ftrackreview-mp4',
				'file_type': component['file_type'],
				'version': version
			})
			review_component['metadata'] = {
				'source_component_id': component['id'],
				'ftr_meta': json.dumps({
					# 'frameIn': 0, 'format': 'h264', "frameRate": 24.0, "frameOut": 421
					# 'frameIn': 0, 'format': 'h264', 'frameRate': fps
					'frameIn': 0, 'format': 'h264', 'frameRate': 24.0
				})
			}

			# Copy data from source to review component.
			source_location = self._session.pick_location(component)
			server_location = self._session.get('Location', ftrack_api.symbol.SERVER_LOCATION_ID)
			resource_identifier = server_location.structure.get_resource_identifier(review_component)
			server_location._add_data(component, resource_identifier, source_location)

			# Register component in server location
			self._session.create(
				'ComponentLocation', data=dict(
					component=review_component,
					location=server_location,
					resource_identifier=resource_identifier
				)
			)

			# Commit before setting thumbnail to ensure thumbnail has been persisted.
			self.commit(self._session)


	# See, asset_selector.py and item_selector.py
	# @async.asynchronous
	def loadAssets(self, entity):
		# IMPORTANT: entity is a Task
		assets = []
		try:
			if entity['object_type']['name'] == 'Task':
				parents = self.getParents(self._session, entity)

			versions = self._session.query('AssetVersion where asset.parent.id like "%s"' % entity['parent_id']).all()
			for version in versions:
				asset = self._session.get('Asset', version['asset_id'])
				if asset:
					assets.append(asset)

			assets = sorted(assets, key=lambda asset: asset['name'])

		except AttributeError:
			self.logger.warning('Unable to fetch assets for entity: %s' % entity)

		return assets


	# See, item_selector.py
	def todo(self):
		asset_types = self.loadAssetTypes()
		# self.logger.debug('asset types: %s' % asset_types)

		# Random sample: asset_types[0],
		# See, asset_options.py
		asset_type = asset_types[0]
		# asset_name = asset_type and asset_type['name'] or ''
		# self.logger.debug('asset_type: %s' % asset_type)
		# self.logger.debug('asset_name: %s' % asset_name)

		# resource identifier
		# file_upload = os.path.join(basedir, 'images', 'TexturesCom_Branches0014_1_alphamasked_S.png')
		# file_upload = os.path.join(basedir, 'images', 'dofpro_diet_cokeDM.jpg')
		# file_upload = os.path.join(basedir, 'video', 'sample_iTunes.mov')
		# file_upload = os.path.join(basedir, 'video', 'TMZ_walk_blocking_v002.mov')
		# file_upload = os.path.join(basedir, 'video', 'TMZ_012_0010.mov')
		# file_upload = os.path.join(basedir, 'video', 'P6090053.mov')
		file_upload = os.path.join(basedir, 'video', 'lalala.mov')

		if sys.platform == 'win32':
			asset_name = file_upload.split('\\')[-1]
		else:
			asset_name = file_upload.split('/')[-1]
		asset_name, ext = os.path.splitext(asset_name)

		# Scenario 1: Suppose already exist assets in ftrack,
		#             which represented by existing self.task
		# IMPORTANT: Display all user tasks in browser and create combobox
		# here for easier, just pick one
		assets = self.loadAssets(self.task)
		if len(assets) == 0:
			asset = None
			self.logger.debug('Asset IS NONE')
		else:
			asset = assets[-1]
			self.logger.debug('HAS ASSET')
		# self.logger.debug('asset: %s' % asset)
		self.publish(self.task, asset, asset_type, asset_name, file_upload)


		self.destroySession(shared=False)




def main(arguments=None):

	if not arguments:
		arguments = []

	parser = argparse.ArgumentParser()

	loggingLevels = dict()
	for level in (
		logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING,
		logging.ERROR, logging.CRITICAL
	):
		loggingLevels[logging.getLevelName(level).lower()] = level

	parser.add_argument(
		'-v', '--verbosity',
		help='Set the logging output verbosity.',
		choices=loggingLevels.keys(),
		default='warning'
	)

	namespace = parser.parse_args(arguments)
	log_setting.configureLogging(
		'batch', level=loggingLevels[namespace.verbosity]
	)

	# Load application
	app = Publisher()
	app.todo()



if __name__ == '__main__':
	# raise SystemExit( main(sys.argv[1:]) )
	main(sys.argv[1:])
