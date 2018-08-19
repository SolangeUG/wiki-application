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
    It aggregates functionalities for retrieving wiki articles from the GAE Datastore, or Memcache.
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


class WikiEditorHandler(handler.TemplateHandler):
    """
    WikiEditorHandler inherits from the hander.TemplateHandler class.
    It aggregates functionalities for creating, editing or persisting wiki articles to the datastore.
    """
    def render_article(self, editionmode=False, title="", content="", error=""):
        self.render("article.html", editionmode=editionmode, title=title, content=content, error=error)

    def get(self):
        article = None
        username = None

        # do we have a logged in user?
        user_cookie = self.request.cookies.get('user')
        if user_cookie:
            username = security.check_secure_val(user_cookie)

            if username:
                # a known user is logged in
                title = self.request.params[0]

                if title:
                    # search for the corresponding title from the memcache
                    articles = memcache.get('top_ten')
                    if articles and len(articles) > 0:
                        for item in articles:
                            if item.title == title:
                                article = item
                                break
                    if article:
                        # edition of an earlier created article
                        self.render_article(editionmode=True, title=article.title, content=article.content)
                    else:
                        # creation of a new article with the presubmitted title
                        self.render_article(editionmode=True, title=title)
                else:
                    # creation of a new article without a presubmitted title
                    self.render_article(editionmode=True)

        if not username:
            # only logged in users are allowed to create/edit articles
            self.redirect('/login')

    def post(self):
        pass


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
        - title : topic/subject of the wiki article
        - content : actual content of the wiki article
        - author: username of the user who created it
        - created : creation date and time of wiki article
        - updated: date and time of last update/modification
    """
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
