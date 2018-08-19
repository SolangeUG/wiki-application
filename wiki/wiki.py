import time
import logging
import util.security as security
import handler.handler as handler
from google.appengine.ext import db
from google.appengine.api import memcache

# log hits to memcache and requests made to the datastore
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class WikiHandler(handler.TemplateHandler):
    """
    WikiHandler inherits from the hander.TemplateHandler class.
    It aggregates functionalities for creating, editing and retrieving wiki articles, using the GAE Datastore.
    """
    def get(self):
        logged = False
        username = None

        # is there a logged in user?
        user_cookie = self.request.cookies.get('user')
        if user_cookie:
            username = security.check_secure_val(user_cookie)
            logged = username is not None

        # retrieve a list of the 10 most recently created or updated articles
        articles = get_top_articles()
        self.render("wiki.html", logged=logged, username=username, articles=articles)


def get_top_articles(update=False):
    """
    Retrieve 10 most recent wiki articles from the datastore or from memcache
    :param update: when this is specified, articles are retrived from the datastore
    :return: a list of 10 most recent articles
    """
    # use caching to avoid running unnecessary DB queries at each page load
    key = 'top_ten'
    articles = memcache.get(key)

    logging.warn('MEMCACHE | Wiki articles %s' % str(articles))

    if (articles is None) or (len(articles) == 0) or update:
        # necessary artificial delay when a new article has just been persisted to the datastore
        if update:
            time.sleep(2)

        articles = db.GqlQuery('SELECT * FROM Article ORDER BY updated DESC LIMIT 10')
        articles = list(articles)
        memcache.set(key, articles)

        logging.warn('DATASTORE | Wiki articles count %s' % str(len(articles)))
    return articles


class Article(db.Model):
    """
    This class inherits from the GAE db.Model (entity) class, and represents a wiki article.
    A wiki article is made of three properties:
        - subject : topic/title of the wiki article
        - content : actual content of the wiki article
        - author: username of the user who created it
        - created : creation date and time of wiki article
        - updated: date and time of last update/modification
    """
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
