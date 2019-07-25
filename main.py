import webapp2
import jinja2
import os
from google.appengine.api import urlfetch, users
from google.appengine.ext import ndb
import json
import datetime

class SiteUser(ndb.Model):
    first_name=ndb.StringProperty()
    email=ndb.StringProperty()
    zip_code=ndb.StringProperty()

def checkLogIn(template):
    logout_url=users.create_logout_url('/')
    user=users.get_current_user()
    if user:    #someone logged into Google = only show logout feature
        template["logout_url"]= logout_url   #need to hide
        template["hideLogIn"]= "hidden=\"\" "
    else:   #not logged into Google = only show login feature
        template["hideLogOut"]= "hidden=\"\" "  #checks if someone is logged in to google and offers the appropriate way out

class MainPage(webapp2.RequestHandler): #inheritance
    def get(self):
        index_template=jinjaEnv.get_template('index.html')
        index_dict={}
        checkLogIn(index_dict)
        self.response.write(index_template.render(index_dict))

class LoginPage(webapp2.RequestHandler):
    def checkExistingUser(self,logout_url):
        user=users.get_current_user()
        email_address=user.nickname()   #username
        existing_user=SiteUser.query().filter(SiteUser.email== email_address).get() #get only pulls 1 record
        if existing_user:
            self.redirect("/")  #send to home
        else:
            self.redirect("/register")   #send to register
    def get(self):
        user=users.get_current_user()

        logout_url=users.create_logout_url('/') #redirect to this link
        if user:    #someone is already logged in to gmail
            self.checkExistingUser(logout_url)
        else:   #not a google user
            login_url=users.create_login_url('/login')

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
            email=user.nickname(),
            zip_code=self.request.get('zip_code')   #need to make sure this is valid
        )
        site_user.put()
        afterRegister_dict={        }
        afterRegister_template=jinjaEnv.get_template('afterRegister.html')
        self.response.write(afterRegister_template.render(afterRegister_dict))

class ShowsResultPage(webapp2.RequestHandler):
    def get(self):
        pass

class MovieResultPage(webapp2.RequestHandler):
    def get(self):  #from getLocation.html
        user=users.get_current_user()
        movie_title=self.request.get('movie_title')
        zip_code=48098#self.request.get('zip_code')
        radius=self.request.get('mile_options') #raidus feature is down rn
        date=datetime.datetime.now().strftime("%Y-%m-%d")

        api_url="http://data.tmsapi.com/v1.1/movies/showings?startDate=%s&zip=%s&api_key=zqhnfqa7uwk9umu23kegjdy8" % (date, zip_code)
        print(api_url)
        gracenote_response_json = urlfetch.fetch(api_url).content
        gracenote_response_raw = json.loads(gracenote_response_json)
        showed_movies=[]
        # print(gracenote_response_raw)
        for movie in gracenote_response_raw:    #need to filter to match movie they selected
            if movie["title"] == movie_title:
                showed_movies.append(movie)
                break   #showed_movies should contain only 0 or 1 movies, but just in case it finds 2
        print(len(showed_movies))
        movie_result_dict={
            "movieInfos": showed_movies,
            "selected_movie": movie_title,
            "found": "1"
        }
        checkLogIn(movie_result_dict)
        # print(showed_movies[0])
        movie_result_template=jinjaEnv.get_template('movie-result.html')
        self.response.write(movie_result_template.render(movie_result_dict))
    def post(self): #post from clicking movie on ResultsPage
        movie_title=self.request.get('movie_title') #form on getLocation.html is not sending this
        # movie_title=movie_title.replace(' ','_')
        user=users.get_current_user()
        get_location_dict={
            "movie_title":movie_title
        }
        logout_url=users.create_logout_url('/')
        if user:    #someone logged into Google = only show logout feature
            get_location_dict["logout_url"]= logout_url   #need to hide
            get_location_dict["hideLogIn"]= "hidden=\"\" "
        else:   #not logged into Google = only show login feature
            get_location_dict["hideLogOut"]= "hidden=\"\" "
        get_location_template=jinjaEnv.get_template('getLocation.html')
        self.response.write(get_location_template.render(get_location_dict))

class ResultsPage(webapp2.RequestHandler):
    def get(self):
        pass
    def post(self):
        #Receives the search from the form on index.html
        searchTerm = self.request.get("searchBar")
        #Makes the searchTerm into a url compatable string
        q = searchTerm.replace(" ","+")
        #Make the tastedivekey and use the URL to retrieve data from the tastedive API
        tastedivekey = "341009-MovieMag-4Y8KEEUH"
        api_url = "https://tastedive.com/api/similar?q=" + q +"&k=" + tastedivekey
        tastedive_response_json = urlfetch.fetch(api_url).content
        tastedive_response_raw = json.loads(tastedive_response_json)

        recommendationList = []
        # print(recommendationList)
        for results in tastedive_response_raw['Similar']['Results'][0:50]:
            recommendationList.append(results["Name"])
        titleAndPic = {}
        urls = []
        #For every item that was recommended by tastedive, we extract all the information from the OMDB database
        for item in recommendationList:
            searchTitle = item.replace(" ", "+")
            #Making the call to the OMDB Api with the correct key and then formatting with json
            OMDBkey = "564669e8"
            OMDBurl = "http://www.omdbapi.com/?t=" + searchTitle + "&apikey=" + OMDBkey
            OMDB_response_json = urlfetch.fetch(OMDBurl).content
            OMDB_response_raw = json.loads(OMDB_response_json)
            posterKey = unicode("Poster")
            # print(OMDB_response_raw[key])
            #This function searches through the return from the OMDB database which includes names, dates, titles, genres
            #And only extracts the poster image
            for key in OMDB_response_raw:
                if key == posterKey:
                    link = OMDB_response_raw[key]
                    urls.append(link)
                    titleAndPic[item] = link
        #Search through the OMDB database for an image for the specific item that was actually search for
        OMDBurl = "http://www.omdbapi.com/?t=" + q + "&apikey=" + OMDBkey
        # print(OMDBurl)
        OMDB_response_json = urlfetch.fetch(OMDBurl).content
        OMDB_response_raw = json.loads(OMDB_response_json)
        #Retrieve the image out of the returned json database
        posterKey = unicode("Poster")
        for key in OMDB_response_raw:
            if key == posterKey:
                searchImg = OMDB_response_raw[key]
        references = {
            "recomendations" : recommendationList,
            "link" : urls,
            "movieAndPoster" : titleAndPic,
            'searched' : searchTerm,
            'searchImg' : searchImg
        }
        checkLogIn(references)
        resultsTemplate=jinjaEnv.get_template('results.html')   #gets that html File
        self.response.write(resultsTemplate.render(references))

app=webapp2.WSGIApplication(
    [
        ('/',MainPage), #tuple
        ('/login',LoginPage),
        ('/results', ResultsPage),
        ('/register',RegisterPage),
        ('/movie-results',MovieResultPage),
        ('/shows-results',ShowsResultPage),
    ],
    debug=True    #parameter 1
)
# curl -d 'template_id=112126428&username=danielkelleycssi&password=cssirocks&text0=thisisthetop&text1=thisisthebottom' https://api.imgflip.com/caption_image
jinjaEnv=jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),  #gives loader = "/Users/cssi/Desktop/cssi-labs/pthon/labs/app-engine"
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)
