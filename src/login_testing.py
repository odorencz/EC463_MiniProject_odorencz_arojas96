from google.appengine.api import users
import webapp2
import urllib

class LoginPage(webapp2.RequestHandler):
    def get(self):
        # Start user_details
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            parameters = { 'username': nickname }
            self.redirect( '/?' + urllib.urlencode( parameters ) )
            logout_url = users.create_logout_url('/')
            greeting = 'Welcome, {}! (<a href="{}">sign out</a>)'.format(
                nickname, logout_url)
        else:
            login_url = users.create_login_url('/')
            greeting = '<a href="{}">Sign in</a>'.format(login_url)
        # End user_details
        self.response.write(
            "<html><body><b>Welcome to Olivia and Andres's sensor viewer!</b><br> {}</body></html>".format(greeting))

class AdminPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                self.response.write('You are an administrator.')
            else:
                self.response.write('You are not an administrator.')
        else:
            self.response.write('You are not an administrator.')

