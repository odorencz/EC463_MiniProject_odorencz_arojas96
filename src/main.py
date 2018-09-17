import os
from google.appengine.api import taskqueue
import cloudstorage
from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import background_thread

import sensors
from datetime import datetime
import webapp2
import jinja2
import login_testing
import urllib
import time
import thread

#import webtest
import main

#PROJECT = os.environ('GCLOUD_PROJECT'

humid_master = '/' + os.environ.get( 'BUCKET_NAME', app_identity.get_default_gcs_bucket_name() ) + '/master_h'
temp_master = '/' + os.environ.get( 'BUCKET_NAME', app_identity.get_default_gcs_bucket_name() ) + '/master_t'
total_users = 0

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
        bucket_name = '/' + bucket_name + '/' + user + '/' + sensor_type + '_' + str( sensor_id )
        return bucket_name

class user(ndb.Model):
	uid = ndb.IntegerProperty()
	email = ndb.StringProperty()
        num_sensor = ndb.IntegerProperty()

class sensor( ndb.Model ):
	sensor_type = ndb.StringProperty( )
	sensorid = ndb.IntegerProperty()
	user = ndb.StringProperty( )

class NewUser( webapp2.RequestHandler ):
    def get( self ):
        global total_users
        username = self.request.get( 'username' )
            
        parameters = { 'username': username }
        template = JINJA_ENVIRONMENT.get_template( 'nouser.html' )
        self.response.write( template.render( parameters ) )
        add = self.request.get( 'yes_add' )
        if add == 'Yes':
            username = self.request.get( 'username' )
            User = user( email = username, num_sensor = 0, uid = total_users )
            User.put()
            total_users = total_users + 1  
            parameters = { 'username': username }
            self.redirect( '/?' + urllib.urlencode( parameters ) )
        elif add == 'No':
            self.redirect( '/#'  )
            
class NewSensor( webapp2.RequestHandler ):
    def get( self ):
        curr_user = users.get_current_user()
        username = curr_user.nickname()

        User = user.query( user.email == username )
        user_profile = User.get()
    
        parameters = { 'username': username,
                        'num_sensor': user_profile.num_sensor }
        template = JINJA_ENVIRONMENT.get_template( 'addsensor.html' )
        self.response.write( template.render( parameters ) )
        add = self.request.get( 'yes_no' )
        if add == 'Yes':
            self.response.write( 'adding' )
            username = users.get_current_user().nickname()
            User = user.query( user.email == username )
            user_profile = User.get()
            uid = user_profile.uid
            sensor_num = user_profile.num_sensor + 1
            
            new_sensor = sensor( sensor_type = 'humidity', sensorid = sensor_num, user = username )
            new_sensor.put()
            humid_path = get_bucket( user = str( uid ), sensor_type = 'h', sensor_id = sensor_num )
            create_file( humid_path )
            
            f = cloudstorage.open( humid_master, "r" )
            contents = f.read()
            f.close()
            f = cloudstorage.open( humid_master, "w" )
            f.write( contents )
            f.write( humid_path )
            f.close()

            new_sensor = sensor( sensor_type = 'temp', sensorid = sensor_num, user = username )
            temp_path = get_bucket( user = str( uid ), sensor_type = 't', sensor_id = sensor_num )
            create_file( temp_path )
            
            f = cloudstorage.open( temp_master, "r" )
            contents = f.read()
            f.close()
            f = cloudstorage.open( temp_master, "w" )
            
            f.write( contents )
            f.write( temp_path )
            f.close()

            new_sensor.put()

            user_profile.num_sensor = user_profile.num_sensor +  1
            user_profile.put()
            parameters = { 'username': username }
            
            self.redirect( '/?' + urllib.urlencode( parameters ) )
        elif add == 'No':
            username = users.get_current_user().nickname()
            parameters = { 'username': username }
            self.redirect( '/?' + urllib.urlencode( parameters ) )

class ViewSensor( webapp2.RequestHandler ):
    def get( self ):
        username = users.get_current_user().nickname()
        logout_url = users.create_logout_url( '/' )
        user_profile = user.query( user.email == username ).get()
        num_sensor = user_profile.num_sensor
        buttons = ""
        template = JINJA_ENVIRONMENT.get_template( 'viewsensor.html' )
        parameters = { 'username': username, 'num_sensor': num_sensor, 'logout': logout_url }
        self.response.write( template.render( parameters ) )

        pick_sensor = self.request.get( 'pick_sensor' )


class MainPage(webapp2.RequestHandler):
	#bucket = get_bucket( 'Olivia' )
	#self.create_file( bucket )
	#self.read_file( bucket )
        ndb.delete_multi( user.query().fetch( keys_only = True ) )
        ndb.delete_multi( sensor.query().fetch( keys_only = True ) )
        def get( self ):
                curr_user = users.get_current_user()
                if not curr_user:
                    self.redirect( '/login' )
                    return
                
            
                logout_url = users.create_logout_url( '/' ) 
                
                template = JINJA_ENVIRONMENT.get_template( 'index.html' )
                username = curr_user.nickname()

                test = user.query( user.email == username )
                user_profile = test.get()
                if not user_profile: 
                    param = { 'username': username }
                    self.redirect( '/newuser/?' + urllib.urlencode( param ) )
                    return

	        num_sensor = user_profile.num_sensor

                parameters = { 'username': username, 'logout': logout_url, 'num_sensor': user_profile.num_sensor }
                self.response.write( template.render( parameters ) )
                return 

           
def create_file( filename ):

    write_retry_params = cloudstorage.RetryParams( backoff_factor = 1.1 )
    with cloudstorage.open( filename, 'w', content_type = 'text/plain', options = 
            { 'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'}, retry_params = write_retry_params) as sensor_file:
        sensor_file.close()

def clearLogs():
    f = cloudstorage.open( humid_master, "w" )
    f.close()
    f = cloudstorage.open( temp_master, "w" )
    f.close()

clearLogs()
found = False
try:
    found =  cloudstorage.stat( humid_master )
except Exception as e:
    found = False

if not found:
    create_file( humid_master )

try:
    found = cloudstorage.stat( temp_master )
except Exception as e:
    found = False

if not found:
    create_file( temp_master )

app = webapp2.WSGIApplication(
    [('/', MainPage), ('/newuser/', NewUser), ('/login', login_testing.LoginPage), ( '/admin/', login_testing.AdminPage )
    , ( '/addsensor/', NewSensor ), ( '/viewsensor/', ViewSensor ), ('/update', sensors.UpdateFileHandler) ], debug = True )


task = taskqueue.add( url = '/test' )

