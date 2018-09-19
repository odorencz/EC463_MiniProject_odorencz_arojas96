# EC463_MiniProject_odorencz_arojas96

Using Google App Engine as a means of developing and hosting a web application, we were able to successfully deploy an app that is capable of letting users setup multiple "sensors" in various rooms of their home to monitor temperature and humidity over the previous 6 hours.

This application was created for EC463 Senior Design for Electrical and Computer Engineers at Boston University in Fall 2018 by Olivia Dorencz and Andres Rojas. As of 09/19/18, the live application is available at https://ec463webappodorenczarojas96.appspot.com.

## About Google App Engine 

[Google App Engine](https://cloud.google.com/appengine/) provides a platform to support web applications that handles the underlying infrastructure so developers can focus on building the applications themselves. The services includes a variety of developer tools, supports many popular languages (e.g. python, java, Node.js, etc.), and allows for seamless scaling. Free trials are available for 1 year that also include $300 in credit for services.

Additional Google services used in this project are [Google Cloud Datastore](https://cloud.google.com/datastore/docs/concepts/overview) (a NoSql based database) and [Google Cloud Storage](https://cloud.google.com/storage/).

## Instructions for use

User must have an account on Google App Engine for development on this program. 

### Install
* Log in to [Google App Engine](https://cloud.google.com/appengine/), create account if necessary
* Create new project or select existing project
* Click "Activate Cloud Shell" in the upper right corner
* `$ git clone https://github.com/odorencz/EC463_MiniProject_odorencz_arojas96 `
* `$ cd EC463_MiniProject_odorencz_arojas96/src `
* Repository should now be available for modification and use
* Use modes described below

### Development mode

Running in development mode allows for faster debugging in a local environment. Debug messages and any print messages are outputted to the console. To run in development mode, run `$ dev_appserver.py .` in the `src` directory.
Web preview is then available on port 8080 of the Cloud Shell.

### Deployment mode

After debugging in development mode, you can deploy the app to allow other users to have access to it. To deploy the app run `$ gcloud app deploy` in the `src` directory. Once loaded, the app will be available to view at https://INSERT_YOUR_PROJECT_NAME_HERE.appspot.com

## Navigating the Application

The image below shows a flow diagram of the control flow throughout the application. The black text in the boxes describes the general function of the page. The white text in the boxes shows the path that page is found on. Arrows represent how users can move between pages, and arrow captions describe the steps necessary to make each transition. Though not displayed, all pages include links to be redirected directly to Home or to logout and be redirected back to the Sign In page.
![alt text](https://github.com/odorencz/EC463_MiniProject_odorencz_arojas96/blob/cloud_test/src/storage/app_flow_chart.jpg)

The first page allows a user to sign in. After they are signed in, the app will check whether the user already exists. If the user does exist, they will be redirected to the home page. If the user does not exist, the user can either create a new user or not. If they do not create a new user, they will be logged out. After creating a new user, they will be directed to the homepage. On the homepage there are options to add a new sensor or view an existing sensor. Adding a new sensor will redirect the user to a new page to confirm they want to add a new sensor. Viewing an existing sensor will redirect them to a page where they can select which sensor to view. If the user goes to view a sensor but does not have any sensors, they will be given the option to be redirected to add a new sensor. After selecting a sensor on the view sensor page, the user is redirected to a graph that shows the most recent data for their sensor. The user must refresh the page to gather new data, and new data is produced once a minute. All pages include links to be redirected directly to the home page or to log out.
