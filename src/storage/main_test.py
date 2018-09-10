import os
import webtest
import main

PROJECT = os.environ( 'GCLOUD_PROJECT' )

def test_get( testbed ):
	main.BUCKET_NAME = PROJECT
	app = webtest.TestApp( main.app )
	response = app.get('/')

	assert response.status_int == 200
	asser 'The demo ran' in response.body
