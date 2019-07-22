import webapp2
import jinja2
import os
from google.appengine.api import urlfetch
import json

class MainPage(webapp2.RequestHandler): #inheritance
    def get(self):  #get request
        # self.response.headers['Content-Type']='text/html; charset=utf-8'
        # self.response.write("welcome.html")
        api_url="https://api.imgflip.com/get_memes"
        imgflip_response=urlfetch.fetch(api_url).content
        imgflip_response_json=json.loads(imgflip_response)  #return dictionary of json type code
        print(imgflip_response_json["data"]["memes"])
        meme_templates=[]
        for meme in imgflip_response_json["data"]["memes"][0:10]:
            meme_templates.append(meme["url"])
        my_template_dict={
            "imgs": meme_templates
        }
        welcomeTemplate=jinjaEnv.get_template('welcome.html')   #gets that html File
        self.response.write(welcomeTemplate.render(my_template_dict))

class LoginPage(webapp2.RequestHandler):
    pass

class MovieResultPage(webapp2.RequestHandler):
    pass

class ShowsResultPage(webapp2.RequestHandler):
    pass

app=webapp2.WSGIApplication(
    [
        ('/',MainPage), #tuple
        ('/login',LoginPage),
        ('/search',SearchPage),
        ('/movie-result',MovieResultPage),
        ('/shows-result',ShowsResultPage),
    ],
    debug=True    #parameter 1
)
# curl -d 'template_id=112126428&username=danielkelleycssi&password=cssirocks&text0=thisisthetop&text1=thisisthebottom' https://api.imgflip.com/caption_image

jinjaEnv=jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),  #gives loader = "/Users/cssi/Desktop/cssi-labs/pthon/labs/app-engine"
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)
