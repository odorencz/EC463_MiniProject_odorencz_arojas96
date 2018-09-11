import os

import cloudstorage
from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.api import users

from datetime import datetime
import webapp2
import jinja2

import urllib

#import webtest
import main

#PROJECT = os.environ('GCLOUD_PROJECT')

cloudstorage.set_default_retry_params(
	cloudstorage.RetryParams(
		initial_delay=0.2, max_delay=5.0, backoff_factor=2, max_retry_period=15)
		)

JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

def get_bucket( user, sensor_type, sensor_id ):
	bucket_name = os.environ.get(
		'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket_name = '/' + bucket_name + '/' + user + '/' + sensor_type + '_' + sensor_id
        return bucket_name

class user(ndb.Model):
	uid = ndb.IntegerProperty()
	email = ndb.StringProperty(  )

class sensor( ndb.Model ):
	sensor_type = ndb.StringProperty( )
	sensorid = ndb.IntegerProperty()
	user = ndb.StringProperty( )

class MainPage(webapp2.RequestHandler):
	#bucket = get_bucket( 'Olivia' )
	#self.create_file( bucket )
	#self.read_file( bucket )
		
        def get( self ):
                found_user = False

                username = self.request.get( 'username' )
                sid = self.request.get( 'sensor_id' )
                
                template = JINJA_ENVIRONMENT.get_template( 'index.html' )
                if username == '':
                    self.response.write( template.render() )
                    return

                
	        User = user( email = username )

                test = user.query( user.email == username )
                
                if not test.get():
                    self.response.write( 'No match found, add user to database?' )
                    template = JINJA_ENVIRONMENT.get_template( 'nouser.html' )
                    template_keys = { 'user': username,
                                      'user_found': False }
                    self.response.render( template.render( template_keys ) )
                    return
                    #User.put()

	        sensor_id = sensor.query( sensor.user == username, sensorid = sid )
                
                if not sensor_id.get():
                    self.response.write( 'No sensors, add new sensor?' )
                    template = JINJA_ENVIRONMENT.get_template( 'nosensor.html' )
                    template_keys = { 'user': username,
                                      'user_found': True }
                    self.response.render( template.render( template_keys )
                    return

                if username == 'newsensor@sensor.com' and not sensor_id.get():
                    self.response.write( 'Creating new sensor for ' + username )
                    new_sensor = sensor( sensor_type = 'humidity', sensorid = 1, user = username )
                    new_sensor.put()

                sensor_find = sensor.query( sensor.user == username )
                found = sensor_find.get()
                stype = 'none'
                if found:
                    stype = found.sensor_type

        	bucket = get_bucket( 'Olivia', 'humid', '1' )
        	self.create_file(bucket)
        	self.read_file(bucket)
                template_values = { 'user': username,
                                    'sensor_id': sid }
		template = JINJA_ENVIRONMENT.get_template( 'index.html' )
		self.response.write( template.render( template_values  ))

            
        def read_file( self, filename ):
                with cloudstorage.open( filename ) as sensor_file:
                        self.response.write( sensor_file.readline() )

        def create_file( self, filename ):
            test = True
           # try:
          #      test = cloudstorage.stat( filename )
         #       return False
        #    except Exception, e:
            #    test = True

            write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
            if test:
                    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with cloudstorage.open(
                            filename, 'w', content_type='text/plain',options={
                            'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                            retry_params=write_retry_params) as sensor_file:
                                sensor_file.write( time )
                                sensor_file.write( 'Cool\n')
                                sensor_file.close()

app = webapp2.WSGIApplication(
	[('/', MainPage)], debug = True )
