import os

import cloudstorage
from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.api import users

from datetime import datetime
import webapp2
import jinja2
import login_testing
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
	email = ndb.StringProperty()
        num_sensor = ndb.IntegerProperty()

class sensor( ndb.Model ):
	sensor_type = ndb.StringProperty( )
	sensorid = ndb.StringProperty()
	user = ndb.StringProperty( )

class NewUser( webapp2.RequestHandler ):
    def get( self ):
        username = self.request.get( 'username' )
        parameters = {'username': username }
        template = JINJA_ENVIRONMENT.get_template( 'nouser.html' )
        self.response.write( template.render( parameters ) )
        add = self.request.get( 'yes_add' )
        if add == 'Yes':
            username = self.request.get( 'username' )
            User = user( email = username )
            User.put()
            parameters = { 'username': username }
            self.redirect( '/?' + urllib.urlencode( parameters ) )
        elif add == 'No':
            self.redirect( '/#'  )
            
class NewSensor( webapp2.RequestHandler ):
    def get( self ):
        username = self.request.get( 'username' )
        parameters = { 'username': username }
        template = JINJA_ENVIRONMENT.get_template( 'nosensor.html' )
        self.response.write( template.render( parameters ) )
        add = self.request.get( 'yes_add' )
        if add == 'Yes':
            username = self.request.get( 'username' )
            new_sensor = sensor( sensor_type = 'humidity', sensorid = '1', user = username )
            new_sensor.put()
            new_sensor = sensor( sensor_type = 'temp', sensorid = '1', user = username )
            new_sensor.put()
            parameters = { 'username': username }
            self.redirect( '/?' + urllib.urlencode( parameters ) )
        elif add == 'No':
            username = self.request.get( 'username' )
            parameters = { 'username': username }
            self.redirect( '/?' + urllib.urlencode( parameters ) )


class MainPage(webapp2.RequestHandler):
	#bucket = get_bucket( 'Olivia' )
	#self.create_file( bucket )
	#self.read_file( bucket )
		
        def get( self ):
                curr_user = users.get_current_user()
                if not curr_user:
                    self.redirect( '/login' )
                    return
                
                self.response.write( 'Currently logged in as ' + curr_user.nickname() )
                username = self.request.get( 'username' )
                logout_url = users.create_logout_url( '/' ) 
                self.response.write( r'<br><a href = "{}" > Sign Out </a>'.format( logout_url ) )
                
                template = JINJA_ENVIRONMENT.get_template( 'index.html' )
                if username == '':
                    self.response.write( template.render() )
                    return

                test = user.query( user.email == username )
                user_profile = test.get()
                if not user_profile: 
                    param = { 'username': username }
                    self.redirect( '/newuser/?' + urllib.urlencode( param ) )
                    return

	        num_sensor = user_profile.num_sensor
                if num_sensor == 0:
                    param = { 'username': username }
                    self.redirect( '/addsensor/?' + urllib.urlencode( param ) )
                
                if not sensor_id.get():
                    template = JINJA_ENVIRONMENT.get_template( 'nosensor.html' )
                    template_keys = { 'user': username,
                                      'user_found': True }
                    self.response.write( template.render( template_keys ) )
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
	[('/', MainPage), ('/newuser/', NewUser), ('/login', login_testing.LoginPage), ( '/admin/', login_testing.AdminPage )], debug = True )
