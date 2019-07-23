import webapp2
import jinja2
import os
from google.appengine.api import urlfetch, users
from google.appengine.ext import ndb
import json

class SiteUser(ndb.Model):
    first_name=ndb.StringProperty()
    age=ndb.IntegerProperty()
    email=ndb.StringProperty()

class MainPage(webapp2.RequestHandler): #inheritance
    def get(self):  #get request
        # self.response.headers['Content-Type']='text/html; charset=utf-8'
        # self.response.write("welcome.html")
        # api_url="https://api.imgflip.com/get_memes"
        # imgflip_response=urlfetch.fetch(api_url).content
        # imgflip_response_json=json.loads(imgflip_response)  #return dictionary of json type code
        # meme_templates=[]
        # for meme in imgflip_response_json["data"]["memes"][0:10]:
        #     meme_templates.append(meme["url"])
        # my_template_dict={
        #     "imgs": meme_templates
        # }
        indexTemplate=jinjaEnv.get_template('index.html')   #gets that html File
        self.response.write(indexTemplate.render())

class LoginPage(webapp2.RequestHandler):

    def get(self):
        user=users.get_current_user()
        if user:
            email_address=user.nickname()   #username
            logout_url=users.create_logout_url('/') #redirect to this link
            logout_button='<a href="%s"> Log out </a>'   % logout_url     #replaces %s with login_url
            existing_user=SiteUser.query().filter(SiteUser.email== email_address).get() #get only pulls 1 record
            if existing_user:
                self.response.write("Welcome to home page "+existing_user.first_name+ logout_button)
            else:
                self.response.write('''Please rgister!
                <form method='post' action='/login'>
                    <input type='text' name='first_name' value="first name">
                    <input type='text' name='age' value="age">
                    <input type='submit'>
                </form>
                <br>
                %s
                ''' % logout_button)
        else:
            login_url=users.create_login_url('/')
            login_button='<a href="%s"> Sign in </a>'   % login_url     #replaces %s with login_url
            self.response.write("Please log in<br>"+ login_button)

    def post(self):
        print("am posting")
        user=users.get_current_user()
        if user:
            site_user=SiteUser(
                first_name=self.request.get('first_name'),
                age=int(self.request.get('age')),
                email=user.nickname()
            )
            site_user.put()
            self.response.write("Thank you for registering")


class MovieResultPage(webapp2.RequestHandler):
    pass

class ShowsResultPage(webapp2.RequestHandler):
    pass
class ResultsPage(webapp2.RequestHandler):
    def get(self):
        pass

    def post(self):
        searchTerm = self.request.get("searchItem")
        q = searchTerm.replace(" ","+")
        k = "341009-MovieMag-4Y8KEEUH"
        api_url = "https://tastedive.com/api/similar?q=" + q +"&k=" + k
        tastedive_response_json = urlfetch.fetch(api_url).content

        tastedive_response_raw = json.loads(tastedive_response_json)

        recommendationList = []
        for results in tastedive_response_raw['Similar']['Results']:
            recommendationList.append(results["Name"])
        references = {
            "recomendations" : recommendationList
        }
        resultsTemplate=jinjaEnv.get_template('results.html')   #gets that html File
        self.response.write(resultsTemplate.render(references))


app=webapp2.WSGIApplication(
    [
        ('/',MainPage), #tuple
        ('/login',LoginPage),
        ('/results', ResultsPage),
        ('/movie-result',MovieResultPage),
        ('/shows-result',ShowsResultPage)
    ],
    debug=True    #parameter 1
)
# curl -d 'template_id=112126428&username=danielkelleycssi&password=cssirocks&text0=thisisthetop&text1=thisisthebottom' https://api.imgflip.com/caption_image

jinjaEnv=jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),  #gives loader = "/Users/cssi/Desktop/cssi-labs/pthon/labs/app-engine"
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)
