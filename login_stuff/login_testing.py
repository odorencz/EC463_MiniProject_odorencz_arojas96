from google.appengine.api import users

#Huge work in progress right now 
user = users.get_current_user()

if user:
    nickname = user.nickname()
    logout_url = users.create_logout_url('/')
    greeting = 'Welcome, {}! (<a href="{}">sign out</a>)'.format(nickname, logout_url)
else:
    login_url = users.create_login_url('/')
    greeting = '<a href="{}">Sign in</a>'.format(login_url)