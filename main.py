import webapp2
import jinja2
import os
from google.appengine.api import urlfetch, users

import json
import datetime
from models import SiteUser,Movie



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
        user=users.get_current_user()
        if user:    #dumb but working way to put a new user in the datastore (idk how to do this from the login page)
            email_address=user.nickname()
            existing_user=SiteUser.query().filter(SiteUser.email==email_address).get()
            if not existing_user:
                existing_user = SiteUser(email=email_address)
                existing_user.put()
        index_template=jinjaEnv.get_template('index.html')
        index_dict={}
        checkLogIn(index_dict)
        self.response.write(index_template.render(index_dict))

class LoginPage(webapp2.RequestHandler):
    def get(self):
        login_url=users.create_login_url('/')
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

class Showtime():
    def __init__(self,dateTime,ticketURI):
        self.dateTime=dateTime.replace('T',' ')
        self.ticketURI=ticketURI

class MovieResultPage(webapp2.RequestHandler):
    def get(self):  #from getLocation.html
        user=users.get_current_user()
        movie_title=self.request.get('movie_title')
        zip_code=48098#self.request.get('zip_code')
        radius=self.request.get('mile_options') #minimum GraceNote allows is 5 mi
        date=datetime.datetime.now().strftime("%Y-%m-%d")

        api_url="http://data.tmsapi.com/v1.1/movies/showings?startDate=%s&zip=%s&api_key=zqhnfqa7uwk9umu23kegjdy8&radius=%s" % (date, zip_code,radius)
        # print(api_url)
        gracenote_response_json = urlfetch.fetch(api_url).content
        gracenote_response_raw = json.loads(gracenote_response_json)
        showed_movie=""
        # print(gracenote_response_raw)
        for movie in gracenote_response_raw:    #need to filter to match movie they selected
            if movie["title"] == movie_title:
                showed_movie=movie
                break   #showed_movies should contain only 0 or 1 movies, but just in case it finds 2
        showtime_dict=self.groupByTheatre(showed_movie)
        movie_result_dict={
            "showtime_dict":showtime_dict,
            "selected_movie": movie_title
        }
        checkLogIn(movie_result_dict)
        # print(showtime_dict)
        movie_result_template=jinjaEnv.get_template('movie-result.html')
        self.response.write(movie_result_template.render(movie_result_dict))
    def groupByTheatre(self,showed_movie):   #return array of Theatres
        if "showtimes" not in showed_movie:
            return {}
        showtimes=showed_movie["showtimes"]
        dict={} #each theatre has many showtimes
        for showtime in showtimes:
            # print(showtime["theatre"]["name"])
            # theatre_name=dict[showtime["theatre"]["name"]]
            if showtime["theatre"]["name"] not in dict:
                dict[showtime["theatre"]["name"]]=[]
            ticketURI=""
            if "ticketURI" in showtime:
                ticketURI=showtime["ticketURI"]
            newShow=Showtime(showtime["dateTime"],ticketURI)
            dict[showtime["theatre"]["name"]].append(newShow)
        # print(dict.items())
        return dict
    def post(self): #post from clicking movie on ResultsPage
        type = self.request.get("type")
        if type == 'TV':
            id = self.request.get("id")
            api_url = "https://api.themoviedb.org/3/tv/" + id + "?api_key=e2648a8f2ae94cef44c1fcfbf7a0f461"
            TMDB_response_json = urlfetch.fetch(api_url).content
            TMDB_response_raw = json.loads(TMDB_response_json)
            # print('***********')
            # print(api_url)
                # user=users.get_current_user()
            genre = []
            creators = []
            runtime = TMDB_response_raw['episode_run_time'][0]
            # print(str(type(runtime)))
            for item in TMDB_response_raw['genres']:
                name = item['name']
                genre.append(name)

            for item in TMDB_response_raw['created_by']:
                name = item['name']
                creators.append(name)
            get_location_dict={
                'type' : 'TV',
                'name' : TMDB_response_raw['original_name'],
                'overview': TMDB_response_raw['overview'],
                'creators' : creators,
                'runtime' : str(TMDB_response_raw['episode_run_time']),
                'poster' : "http://image.tmdb.org/t/p/w185" + TMDB_response_raw['poster_path'],
                'genre' : genre,
                'rating' : TMDB_response_raw['vote_average'],
                'seasons' : TMDB_response_raw['number_of_seasons'],
                'runtime' : runtime
            }
        else:
            id = self.request.get("id")
            api_url = "https://api.themoviedb.org/3/movie/" + id + "?api_key=e2648a8f2ae94cef44c1fcfbf7a0f461"
            TMDB_response_json = urlfetch.fetch(api_url).content
            TMDB_response_raw = json.loads(TMDB_response_json)
            # print(TMDB_response_raw)
            movie_title=self.request.get('movie_title') #form on getLocation.html is not sending this
            # movie_title=movie_title.replace(' ','_')
            user=users.get_current_user()
            genre = []
            for item in TMDB_response_raw['genres']:
                name = item['name']
                genre.append(name)
            get_location_dict={
                'type' : 'Movie',
                "movie_title":movie_title,
                "movie_info" : TMDB_response_raw,
                'name' : TMDB_response_raw['original_title'],
                'overview': TMDB_response_raw['overview'],
                'poster' : "http://image.tmdb.org/t/p/w185" + TMDB_response_raw['poster_path'],
                'genre' : genre,
                'runtime' : TMDB_response_raw['runtime'],
                'release_date' : TMDB_response_raw['release_date'],
                'rating' : TMDB_response_raw['vote_average']

            }
        # print(get_location_dict)
        # print(type)
        checkLogIn(get_location_dict)
        get_location_template=jinjaEnv.get_template('getLocation.html')
        self.response.write(get_location_template.render(get_location_dict))

class ResultsPage(webapp2.RequestHandler):
    def get(self):
        pass
    def post(self):
        #Receives the search from the form on index.html
        # searchDict = self.request.get("searchBar")
        date = self.request.get("date")
        searchTerm = self.request.get("id")
        searchTitle = self.request.get("title")
        searchImg = self.request.get("poster")
        type = self.request.get("type")
        if type == "TV":
            if (date < "2019"): #Use Tastedive for recommendations
                q = searchTitle.replace(" ","+")
                tastedivekey = "341009-MovieMag-4Y8KEEUH"
                api_url = "https://tastedive.com/api/similar?q=" + q +"&k=" + tastedivekey + "&limit=100"
                tastedive_response_json = urlfetch.fetch(api_url).content
                tastedive_response_raw = json.loads(tastedive_response_json)
                tasteDiveRecommendationList = []
                for results in tastedive_response_raw['Similar']['Results'][0:25]:
                    tasteDiveRecommendationList.append(results["Name"])
                recommendationList = []
                # print(tasteDiveRecommendationList)
                for item in tasteDiveRecommendationList:
                    q = item.replace(" ", "+")
                    TMDBkey = "e2648a8f2ae94cef44c1fcfbf7a0f461"
                    api_url = "https://api.themoviedb.org/3/search/tv?api_key=" + TMDBkey +"&query=" + q
                    TMDB_response_json = urlfetch.fetch(api_url).content
                    TMDB_response_raw = json.loads(TMDB_response_json)
                    movies = {}
                    print(api_url)
                    if TMDB_response_raw['total_results']==0 or TMDB_response_raw["results"][0]['poster_path']is None:  #if no poster path, just leave this film out
                        continue
                    movies["title"] = TMDB_response_raw['results'][0]['name']
                    movies["id"] = TMDB_response_raw["results"][0]['id']
                    movies["poster"] = "http://image.tmdb.org/t/p/w185" + TMDB_response_raw["results"][0]['poster_path']
                    recommendationList.append(movies)
                #Makes the searchTerm into a url compatable string
                # q = searchTerm.replace(" ","+")
                #Make the tastedivekey and use the URL to retrieve data from the tastedive API
            else:
                TMDBkey = "e2648a8f2ae94cef44c1fcfbf7a0f461"
                api_url = "https://api.themoviedb.org/3/tv/" + searchTerm + "/similar?api_key=" + TMDBkey
                TMDB_response_json = urlfetch.fetch(api_url).content
                TMDB_response_raw = json.loads(TMDB_response_json)
                recommendationList = []
                for item in TMDB_response_raw["results"]:
                    if item['poster_path'] == None:
                        continue
                    title = item['name']
                    photo = item['poster_path']
                    id = item['id']
                    photoURL = "http://image.tmdb.org/t/p/w185" + photo
                    movieDict = {}
                    movieDict["title"] = title
                    movieDict["poster"] = photoURL
                    movieDict["id"] = id
                    recommendationList.append(movieDict)
                # print("TMDB")
        else:
            if (date < "2019"): #Use Tastedive for recommendations
                q = searchTitle.replace(" ","+")
                tastedivekey = "341009-MovieMag-4Y8KEEUH"
                api_url = "https://tastedive.com/api/similar?q=" + q +"&k=" + tastedivekey
                tastedive_response_json = urlfetch.fetch(api_url).content
                tastedive_response_raw = json.loads(tastedive_response_json)
                tasteDiveRecommendationList = []
                for results in tastedive_response_raw['Similar']['Results'][0:50]:
                    tasteDiveRecommendationList.append(results["Name"])
                recommendationList = []
                for item in tasteDiveRecommendationList:
                    q = item.replace(" ", "+")
                    TMDBkey = "e2648a8f2ae94cef44c1fcfbf7a0f461"
                    api_url = "https://api.themoviedb.org/3/search/movie?api_key=" + TMDBkey +"&query=" + q
                    # print(api_url)
                    TMDB_response_json = urlfetch.fetch(api_url).content
                    TMDB_response_raw = json.loads(TMDB_response_json)
                    movies = {}
                    # print(TMDB_response_raw)
                    if TMDB_response_raw['total_results']==0 or TMDB_response_raw["results"][0]['poster_path']is None:  #if no poster path, just leave this film out
                        continue
                    movies["title"] = TMDB_response_raw["results"][0]['title']
                    movies["id"] = TMDB_response_raw["results"][0]['id']
                    movies["poster"] = "http://image.tmdb.org/t/p/w185" + TMDB_response_raw["results"][0]['poster_path']
                    recommendationList.append(movies)
                # print("tastedive")
                #Makes the searchTerm into a url compatable string
                # q = searchTerm.replace(" ","+")
                #Make the tastedivekey and use the URL to retrieve data from the tastedive API
            else:
                TMDBkey = "e2648a8f2ae94cef44c1fcfbf7a0f461"
                api_url = "https://api.themoviedb.org/3/movie/" + searchTerm + "/similar?api_key=" + TMDBkey
                TMDB_response_json = urlfetch.fetch(api_url).content
                TMDB_response_raw = json.loads(TMDB_response_json)
                recommendationList = []
                for item in TMDB_response_raw["results"]:
                    if item['poster_path'] == None:
                        continue
                    title = item['title']
                    photo = item['poster_path']
                    id = item['id']
                    photoURL = "http://image.tmdb.org/t/p/w185" + photo
                    movieDict = {}
                    movieDict["title"] = title
                    movieDict["poster"] = photoURL
                    movieDict["id"] = id
                    recommendationList.append(movieDict)
                # print("TMDB")
        references = {
            "recomendations" : recommendationList,
            'searched' : searchTitle,
            'searchImg' : searchImg,
            'type' : type

         }
        checkLogIn(references)
        resultsTemplate=jinjaEnv.get_template('results.html')   #gets that html File
        self.response.write(resultsTemplate.render(references))

class VerifyPage(webapp2.RequestHandler):
    def post(self):
        switch = self.request.get("switch")
        # print(switch)
        if switch == "TV":
            type = "TV"
            searchTerm = self.request.get("searchBar")
                        #Makes the searchTerm into a url compatable string
            q = searchTerm.replace(" ","+")
            TMDBkey = "e2648a8f2ae94cef44c1fcfbf7a0f461"
            api_url = "https://api.themoviedb.org/3/search/tv?api_key=" + TMDBkey +"&query=" + q
            TMDB_response_json = urlfetch.fetch(api_url).content
            TMDB_response_raw = json.loads(TMDB_response_json)
            # print(TMDB_response_raw)
            possibleMovies = []
            for item in TMDB_response_raw["results"]:
                if item['poster_path'] == None:
                    continue
                title = item['name']
                photo = item['poster_path']
                id = item['id']
                date = item['first_air_date']
                photoURL = "http://image.tmdb.org/t/p/w185" + photo
                movieDict = {}
                movieDict["title"] = title
                movieDict["poster"] = photoURL
                movieDict["id"] = id
                movieDict["date"] = date
                possibleMovies.append(movieDict)
        else:
            type = "MOVIE"
            searchTerm = self.request.get("searchBar")
            #Makes the searchTerm into a url compatable string
            q = searchTerm.replace(" ","+")
            TMDBkey = "e2648a8f2ae94cef44c1fcfbf7a0f461"
            api_url = "https://api.themoviedb.org/3/search/movie?api_key=" + TMDBkey +"&query=" + q
            TMDB_response_json = urlfetch.fetch(api_url).content
            TMDB_response_raw = json.loads(TMDB_response_json)
            possibleMovies = []
            for item in TMDB_response_raw["results"]:
                if item['poster_path'] == None:
                    continue
                title = item['title']
                photo = item['poster_path']
                id = item['id']
                date = item['release_date']
                photoURL = "http://image.tmdb.org/t/p/w185" + photo
                movieDict = {}
                movieDict["title"] = title
                movieDict["poster"] = photoURL
                movieDict["id"] = id
                movieDict["date"] = date
                possibleMovies.append(movieDict)
        references = {
            "possibleMovies" : possibleMovies,
            "type" : type
        }
        checkLogIn(references)
        verifyTemplate=jinjaEnv.get_template('verify.html')   #gets that html File
        self.response.write(verifyTemplate.render(references))

class MyAccountPage(webapp2.RequestHandler):
    def makeMovieList(self,list):
        res=[] #will be filled with dictionaries representing Movies
        for movie_key in list:
            movieData=movie_key.get()
            movie={
                "title": movieData.title,
                "id": movieData.id,
                "poster": movieData.posterURL
            }
            res.append(movie)
        return res

    def get(self):
        user=users.get_current_user()
        email_address=user.nickname()
        existing_user=SiteUser.query().filter(SiteUser.email==email_address).get()
        if not existing_user:
            self.redirect('/')
            return
        # print(existing_user.toWatchList)
        toWatchList=self.makeMovieList(existing_user.toWatchList)
        seenMovies=self.makeMovieList(existing_user.seenMovies)
        my_account_dict={
            "toWatchList": toWatchList,
            "seenMovies": seenMovies
        }
        checkLogIn(my_account_dict)
        my_account_template=jinjaEnv.get_template('myAcct.html')
        self.response.write(my_account_template.render(my_account_dict))

class UpdateMyAccount(webapp2.RequestHandler):
    def post(self):
        # print("called post UpdateMyAccount")
        user=users.get_current_user()
        email_address=user.nickname()
        existing_user=SiteUser.query().filter(SiteUser.email==email_address).get()
        # print(email_address)

        movie_title=self.request.get("movie_title")
        movie_id=self.request.get("movie_id")
        movie_poster=self.request.get("movie_poster")
        type=self.request.get("type")
        # print("888888"+type)
        movie=Movie(title=movie_title, id=movie_id,posterURL=movie_poster,type=type)
        # print(movie)
        existing_movie=Movie.query().filter(Movie.id==movie_id).get()
        movie_key=""
        if not existing_movie:
            movie_key=movie.put()
        else:
            movie_key=existing_movie.key
        print(movie_key)
        if movie_key in existing_user.toWatchList or movie_key in existing_user.seenMovies:
            return
        # print(existing_users)
        existing_user.toWatchList.append(movie_key)
        # print(existing_user.toWatchList)
        existing_user.put()

class MarkSeenMovie(webapp2.RequestHandler):
    def post(self):
        # print("called post UpdateMyAccount")
        user=users.get_current_user()
        email_address=user.nickname()
        existing_user=SiteUser.query().filter(SiteUser.email==email_address).get()

        movie_title=self.request.get("movie_title")
        movie_id=self.request.get("movie_id")
        movie_poster=self.request.get("movie_poster")
        # print(movie_title)
        movie=Movie.query().filter(Movie.id==movie_id).get()
        movie_key=movie.key
        existing_user.seenMovies.append(movie_key)
        existing_user.toWatchList.remove(movie_key)
        # print(existing_user.seenMovies)
        # print(existing_user.toWatchList)
        existing_user.put()

app=webapp2.WSGIApplication(
    [
        ('/',MainPage), #tuple
        ('/login',LoginPage),
        ('/results', ResultsPage),
        ('/movie-results',MovieResultPage),
        ('/shows-results',ShowsResultPage),
        ('/verify', VerifyPage),
        ('/my-account',MyAccountPage),
        ('/updateMyAccount',UpdateMyAccount),
        ('/markSeenMovie',MarkSeenMovie)
    ],
    debug=True    #parameter 1
)
# curl -d 'template_id=112126428&username=danielkelleycssi&password=cssirocks&text0=thisisthetop&text1=thisisthebottom' https://api.imgflip.com/caption_image
jinjaEnv=jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),  #gives loader = "/Users/cssi/Desktop/cssi-labs/pthon/labs/app-engine"
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)
