import os

import cloudstorage
from google.appengine.api import app_identity

import datetime
import webapp2

import webtest
import main

PROJECT = os.environ('GCLOUD_PROJECT')

cloudstorage.set_default_retry_params(
	cloudstorage.RetryParams(
		initial_delay=0.2, max_delay=5.0, backoff_factor=2, max_retry_period=15)
		))

def get_bucket( user ):
	bucket_name = os.environ.get(
		'BUCKET_NAME', app_identity.get_default_gcs_bucket_name()) + '/' +\
		user.userid )

def read_file( filename )
	with cloudstorage.open( filename ) as sensor_file:
		self.response.write( sensor_file.readline() )

def create_file( filename )
	test = False
	try:
		test =  cloudstorage.stat( filename )
	except cloudstorage_errors.NotFoundError as e:
		test = False
		return
	
	if test:
		time = datetime.now()
		with cloudstorage.open(
			filename, 'w', content_type='text/plain', options={
			'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
			retry_params=write_retry_params) as sensor_file:
				sensor_file.write( time )
				sensor_file.write( 'Cool\n' )
				sensor_file.close()


class MainPage(webapp2.RequestHandler):
	bucket = get_bucket( 'Olivia' )
	create_file( bucket )
	read_file( bucket )

app = webapp2.WSGIApplication(
	[('/', MainPage)], debuge = True )
