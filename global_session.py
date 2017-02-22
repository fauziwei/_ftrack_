# coding: utf-8
# fauziwei@yahoo.com

import os
import logging
import ftrack_api

_shared_session = None
_private_session = None

def destroySession(shared=True):

	# Shared session
	if shared:
		logger = logging.getLogger('batch:session.destroy_[shared]_session')
		global _shared_session

		if _shared_session:
			del _shared_session
			_shared_session = None

	# Private session
	else:
		logger = logging.getLogger('batch:session.destroy_[private]_session')
		global _private_session

		if _private_session:
			del _private_session
			_private_session = None


def getSession(shared=True):

	# Shared session
	if shared:
		logger = logging.getLogger('batch:session.get_[shared]_session')
		global _shared_session

		if not _shared_session:
			_shared_session = ftrack_api.Session(
				server_url=os.environ['FTRACK_SERVER'],
				api_key=os.environ['FTRACK_APIKEY'],
				api_user=os.environ['LOGNAME']
			)
		return _shared_session

	# Private session
	else:
		logger = logging.getLogger('batch:session.get_[private]_session')
		global _private_session

		if not _private_session:
			_private_session = ftrack_api.Session(
				server_url=os.environ['FTRACK_SERVER'],
				api_key=os.environ['FTRACK_APIKEY'],
				api_user=os.environ['LOGNAME'],
				auto_connect_event_hub=False
			)
		return _private_session
