#***********************************************************************************
# Author: Sarah Harber
# Class: CS 496
# Decsription: OAuth 2.0 Implementation Assignment
#***********************************************************************************

from google.appengine.ext import ndb
from google.appengine.api import app_identity
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
import os
import webapp2
import json
import google.appengine.api.urlfetch as urlfetch
import client_secrets
import string
import random
import logging
import urllib


#***********************************************************************************
# Get Client Secret From Auth File
CLIENT_SECRET = client_secrets.CLIENT_SECRET
# Get Client ID From Auth File
CLIENT_ID = client_secrets.CLIENT_ID
# Set OAuth URL
OAUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
# Set Home URL
HOME_URL = "https://cs496-harbers-oauth.appspot.com/"
# Redirect URL
REDIRECT_URL = "https://cs496-harbers-oauth.appspot.com/oauth"

# Create Random State
state = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])

# Set Request URL
request_url = OAUTH_URL + '?response_type=code&' + \
                'client_id=' + CLIENT_ID +'&' + \
                'redirect_uri=' + "https://cs496-harbers-oauth.appspot.com/oauth" + '&' + \
                'scope=email&' + 'state=' + state 

# Set Other template values to N/A
first_name = "N/A"
last_name = "N/A" 
google_plus_url = "N/A" 
status = "N/A" 

# Set Path for Index.html
path = os.path.join(os.path.dirname(__file__), 'templates/index.html')


# OAuthHandler - Gets user's first name, last name, 
# 				 URL for Google + And State Code
class OAuthHandler(webapp2.RequestHandler):
	def get(self):	
		CODE = self.request.GET['code']
		first_name = CODE;
		STATE = self.request.GET['state']
		data = {
			'code': CODE,
			'client_id': CLIENT_ID,
			'client_secret': CLIENT_SECRET,
			'redirect_uri': REDIRECT_URL,
			'grant_type': 'authorization_code'
			}
		send_values = urllib.urlencode(data)
		header = {'Content-Type':'application/x-www-form-urlencoded'}
		req = urlfetch.fetch(url="https://www.googleapis.com/oauth2/v4/token", payload=send_values,  headers=header, method=urlfetch.POST )
		response = json.loads(req.content)
		
		# Set header for GET REQUEST
		header = {'Authorization': 'Bearer ' + response['access_token']}
		
		# Request Information Needed for website
		final_request = urlfetch.fetch(url="https://www.googleapis.com/plus/v1/people/me",  headers=header, method=urlfetch.GET)

	  # Loads the JSON data into a Variable
		data_received = json.loads(final_request.content)

		# Save Variable information needed for website
		first_name = data_received['name']['givenName']
		last_name = data_received['name']['familyName']
		google_plus_url = str(data_received['url'])
		sendvars = {'request_url': request_url,
											 'f_name': first_name,
											 'l_name': last_name,
											 'google_url': google_plus_url,
											 'final_state': STATE}
		self.response.out.write(template.render(path, sendvars))
		return;

# Mainpage Code To start Google OAuth 2.0 Process
class MainPage(webapp2.RequestHandler):
	def get(self):
		# Send Template with Values
		self.response.out.write(template.render(path, {'request_url': request_url,
											 'f_name': first_name,
											 'l_name': last_name,
											 'google_url': google_plus_url,
											 'final_state': status}))

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/oauth', OAuthHandler)
], debug=True)
