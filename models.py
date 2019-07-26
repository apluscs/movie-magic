
from google.appengine.ext import ndb
class SiteUser(ndb.Model):
    first_name=ndb.StringProperty()
    email=ndb.StringProperty()
    zip_code=ndb.StringProperty()
    watchedMovies = ndb.StringProperty(repeated = True)

class Movie(ndb.Model):
    name = ndb.StringProperty(required = True)

class Liked(ndb.Model):
    siteuser = ndb.KeyProperty(SiteUser)
    movie = ndb.KeyProperty(Movie)
