
from google.appengine.ext import ndb

class Movie(ndb.Model):
    title = ndb.StringProperty()
    id=ndb.StringProperty()
    posterURL=ndb.StringProperty()
    type=ndb.StringProperty()


class SiteUser(ndb.Model):
    email=ndb.StringProperty()
    toWatchList=ndb.KeyProperty(Movie,repeated=True)
    seenMovies = ndb.KeyProperty(Movie,repeated = True)


# class Liked(ndb.Model):
#     siteuser = ndb.KeyProperty(SiteUser)
#     movie = ndb.KeyProperty(Movie)
