import os
import urllib

import jinja2
import webapp2

from google.appengine.api import users

from bigquery import get_client

json_key = 'serviceaccount.json'


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'

            query = "SELECT FLIGHTNO, CP, FO, UA, HL, DL FROM demo.sdata WHERE CP IN (SELECT latamid FROM demo.mapping WHERE userid='%s')" % (user)
            client = get_client(json_key_file=json_key, readonly=True)
            try:
                job_id, results = client.query(query, timeout=10)
            except BigQueryTimeoutException:
                print "Timeout"

            template_values = {
                'user': user,
                'url': url,
                'url_linktext': url_linktext,
                'results': results,
            }

            template = JINJA_ENVIRONMENT.get_template('index.html')
        
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            template = JINJA_ENVIRONMENT.get_template('nologin.html')

        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
