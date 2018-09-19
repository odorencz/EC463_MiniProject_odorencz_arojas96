import datetime
import cloudstorage
import random
import os
import time
import webapp2
from google.appengine.api import background_thread
from google.appengine.api import app_identity
class HumiditySensor():
    def __init__( self, path ):
        self.path = path
        self.base_humid = random.uniform( 0, 100 )

    def writeData( self ):
        f = cloudstorage.open( self.path, "r" )
    
        file_contents = []
        count = 2160
        num_lines = 0
        line = f.readline()
        while line:
            if len( line ) > 5:
                file_contents.append( line )
                num_lines = num_lines + 1
            line = f.readline()

        f.close()
        

        f = cloudstorage.open( self.path, "w" )
        lastline = ""
        lasttime = ""
        lasthumid = ""

        offset = num_lines - count
        if offset < 0:
            offset = 0

        for i in range( offset, num_lines ):
            f.write( file_contents[ i ] )
            f.write( '\n' )
            lastline = line

        if lastline == "":
            lasthumid = str( self.base_humid )
        else:
            lasttime, lasthumid = lastline.split(",")

        new_value = random.uniform( -5, 5 ) + float( lasthumid )

        if new_value > 100:
            new_value = 100
        elif new_value < 0:
            new_value = 0
        
        f.write( datetime.datetime.now().time().strftime( "%d:%m:%y" ) + ',' + str( new_value ) )
        
        f.close()

class TempSensor():
    def __init__( self, path ):
        self.path = path
        self.base_temp = random.randint( 0, 90 )


    def writeData( self ):
        f = cloudstorage.open( self.path, "r" )

    
        file_contents = []
        count = 2160
        num_lines = 0

        line = f.readline()
        while line:
            if len( line ) > 5:
                file_contents.append( line )
                num_lines = num_lines + 1
            line = f.readline()

        f.close()
    

        f = cloudstorage.open( self.path, "w" )
        lastline = ""
        lasttemp = ""
        lasttime = ""
        offset = num_lines - count
        if offset < 0:
            offset = 0

        for i in range( offset, num_lines ):
            f.write( file_contents[ i ] )
            f.write( '\n' )
            lastline = line

        if lastline == "":
            lasttemp = str( self.base_temp )
        else:
            lasttime, lasttemp = lastline.split( "," )

        new_value = random.uniform( -5, 5 ) + float( lasttemp )
        f.write( datetime.datetime.now().time().strftime( "%d:%m:%y" ) + ',' + str( new_value ) )
        
        f.close()

humid_master = '/' + os.environ.get( 'BUCKET_NAME', app_identity.get_default_gcs_bucket_name() ) + '/master_h'
temp_master = '/' + os.environ.get( 'BUCKET_NAME', app_identity.get_default_gcs_bucket_name() ) + '/master_t'

humidList = []
tempList = []

humidObjList = []
tempObjList = []

def wait_update():
    f = cloudstorage.open( humid_master, 'r' )
    humid_added = len( humidList )
    temp_added = len ( tempList )
    
    contents = f.read()
    for file_name in contents.split( ';' ):
        if file_name not in humidList and len(file_name)>5:
            humidList.append( file_name )
            new_humid = HumiditySensor( path = file_name )
            humidObjList.append( new_humid )
            humid_added = humid_added + 1
    f.close()

    f = cloudstorage.open( temp_master, 'r' )
    contents = f.read()
    for file_name in contents.split( ';' ):
        if file_name not in tempList and len(file_name)>5:
            tempList.append( file_name )
            new_temp = TempSensor( path = file_name )
            tempObjList.append( new_temp )
            temp_added = temp_added + 1
    f.close()

    
    for i in humidObjList:
        i.writeData()
    for i in tempObjList:
        i.writeData()

class UpdateFileHandler( webapp2.RequestHandler ):
    def post( self ):
        while( True ):
            wait_update()
            time.sleep( 10 )

app = webapp2.WSGIApplication( [ ('/test', UpdateFileHandler) ], debug = True )

