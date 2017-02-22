# coding: utf-8
'''Fauzi, fauzi@soovii.com'''

import os
import sys
import logging
import argparse
import urllib
import urllib2
import ftrack_api.entity.location
import ftrack_api.event.base
import config
import global_session
import async
import log_setting

basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(basedir)

ftrack_api.symbol.SERVER_LOCATION_ID

class Download:

	def __init__(self):

		self.logger = logging.getLogger(__name__ + '.' + self.__class__.__name__)
		# Shared session
		# self.session = global_session.getSession(shared=True)
		# Private session
		self._session = global_session.getSession(shared=False)

		# Tester task
		self.task_id = '80b30930-d7e1-11e6-9347-14187740b71a'
		self.task = self._session.get('Task', self.task_id)

	def destroySession(self, shared=True):
		global_session.destroySession(shared)

	def commit(self, session):
		try:
			session.commit()
		except:
			session.rollback()

	def getThumbnail(self, component_id):
		'''Get a url to the thumbnail.'''
		params = urllib.urlencode({
			'id': component_id,
			'username': os.environ.get('LOGNAME', 'nouser'),
			'apiKey': os.environ.get('FTRACK_APIKEY', 'no-key-found')
		})
		url = '{baseUrl}/component/thumbnail?{params}'.format(
			baseUrl=os.environ['FTRACK_SERVER'], params=params
		)
		return url

	def getAttachmentUrl(self, component_id):
		'''Return authenticated URL to attachment component with *component_id*'''
		params = urllib.urlencode({
			'id': component_id,
			'username': os.environ.get('LOGNAME', 'nouser'),
			'apiKey': os.environ.get('FTRACK_APIKEY', 'no-key-found')
		})
		url = '{baseUrl}/component/get?{params}'.format(
			baseUrl=os.environ['FTRACK_SERVER'], params=params
		)
		return url

	def loadComponents(self, task_id):
		versions = self._session.query('AssetVersion where task_id like "%s"' % task_id).all()
		for version in versions:
			components = self._session.query('Component where version_id like "%s"' % version['id']).all()
			for component in components:
				component['file_type']

				filename = '%s%s' % (component['name'], component['file_type'])
				# Download real attachment
				url = self.getAttachmentUrl(component['id'])
				# urllib.urlretrieve(url, os.path.join(basedir, filename))
				try:
					resp = urllib2.urlopen(url)
					with open(os.path.join(basedir, filename), 'wb') as file:
						file.write(resp.read())
				except urllib2.URLError as error:
					print 'urllib2: %s' % error
				except urllib2.HTTPError as error:
					print 'urllib2: %s' % error
				except:
					print 'urllib2 error download.'


				# Download thumbnail | only images filename
				# thumbnail = '%s_thumb%s' % (component['name'], component['file_type'])
				# url = self.getThumbnail(component['id'])
				# urllib.urlretrieve(url, 'this_thumb.jpg')



	def todo(self):
		self.loadComponents(self.task_id)
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
	app = Download()
	app.todo()



if __name__ == '__main__':
	# raise SystemExit( main(sys.argv[1:]) )
	main(sys.argv[1:])
