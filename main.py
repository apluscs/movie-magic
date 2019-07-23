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
    def get(self):
        user=users.get_current_user()
        print(user)
        logout_url=users.create_logout_url('/')
        index_template=jinjaEnv.get_template('index.html')
        index_dict={}
        if user:    #someone logged into Google = only show logout feature
            index_dict={
                "logout_url": logout_url,    #need to hide
                "hideLogIn": "hidden=\"\" "
            }
        else:   #not logged into Google = only show login feature
            index_dict={
                "hideLogOut": "hidden=\"\" "
            }
        print(index_dict)
        self.response.write(index_template.render(index_dict))

class LoginPage(webapp2.RequestHandler):
    def checkExistingUser(self,logout_url):
        user=users.get_current_user()
        email_address=user.nickname()   #username
        existing_user=SiteUser.query().filter(SiteUser.email== email_address).get() #get only pulls 1 record
        if existing_user:
            self.redirect("/?logout_url="+logout_url)  #send to home
        else:
            self.redirect("/register")   #send to register
    def get(self):
        user=users.get_current_user()
        print(user)
        logout_url=users.create_logout_url('/') #redirect to this link
        if user:    #someone is already logged in to gmail
            self.checkExistingUser(logout_url)
        else:   #not a google user
            login_url=users.create_login_url('/login')
            print(login_url)
            login_dict={
                "login_url": login_url
            }
            login_template=jinjaEnv.get_template('login.html')
            self.response.write(login_template.render(login_dict))



class RegisterPage(webapp2.RequestHandler):
    def get(self):
        logout_url=users.create_logout_url('/')
        registerTemplate=jinjaEnv.get_template('register.html')
        register_dict={ #need to accept logout_url
            "logout_url": logout_url
        }
        self.response.write(registerTemplate.render(register_dict))
    def post(self):
        user=users.get_current_user()
        site_user=SiteUser(
            first_name=self.request.get('first_name'),
            age=int(self.request.get('age')),
            email=user.nickname()
        )
        site_user.put()
        afterRegister_dict={        }
        afterRegister_template=jinjaEnv.get_template('afterRegister.html')
        self.response.write(afterRegister_template.render(afterRegister_dict))

class MovieResultPage(webapp2.RequestHandler):
    pass

class ShowsResultPage(webapp2.RequestHandler):
    pass

class ResultsPage(webapp2.RequestHandler):
    def get(self):
        pass
    def post(self):
        searchTerm = self.request.get("searchBar")
        q = searchTerm.replace(" ","+")
        tastedivekey = "341009-MovieMag-4Y8KEEUH"
        api_url = "https://tastedive.com/api/similar?q=" + q +"&k=" + tastedivekey
        tastedive_response_json = urlfetch.fetch(api_url).content
        tastedive_response_raw = json.loads(tastedive_response_json)
        recommendationList = []
        for results in tastedive_response_raw['Similar']['Results'][0:10]:
            recommendationList.append(results["Name"])
        titleAndPic = {}
        urls = []
        for item in recommendationList:
            searchTitle = item.replace(" ", "+")
            OMDBkey = "564669e8"
            OMDBurl = "http://www.omdbapi.com/?t=" + searchTitle + "&apikey=" + OMDBkey
            OMDB_response_json = urlfetch.fetch(OMDBurl).content
            OMDB_response_raw = json.loads(OMDB_response_json)
            posterKey = unicode("Poster")
            # print(OMDB_response_raw[key])
            for key in OMDB_response_raw:
                if key == posterKey:
                    link = OMDB_response_raw[key]
                    urls.append(link)
                    titleAndPic[item] = link
        print (titleAndPic)
            # url = OMDB_response_raw["Poster"]
            # print("****************************")
            # for key in OMDB_response_raw:
            #     print("key is " + str(key))
            #     print("key type is" + str(type(key)))
            #     print("value is " + str(OMDB_response_raw[key]))

            # print("type is " + OMDB_response_raw)
            # print(OMDB_response_raw.keys())
            # titleAndPic[item] = url
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
