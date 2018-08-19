import time
import logging
import util.security as security
import handler.handler as handler
from google.appengine.ext import db
from google.appengine.api import memcache

# log hits to memcache and requests made to the datastore
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class ArticleHandler(handler.TemplateHandler):
    """
    ArticleHandler inherits from the handler.TemplateHandler class.
    It aggregates functionalities for retrieving or creating a requested resource by the user.
    """

    def render_article(self, logged=False, username=None, editionmode=False, article=None, error=""):
        self.render("article.html", logged=logged, username=username,
                    editionmode=editionmode, article=article, error=error)

    def get(self, title):
        # do we have a logged in user?
        logged = False
        username = None

        user_cookie = self.request.cookies.get('user')
        if user_cookie:
            username = security.check_secure_val(user_cookie)
            logged = username is not None

        # do we have a non-empty title?
        if title:
            article = get_article(title)
            if article:

                self.render("article.html", logged=logged, username=username, article=article)
            else:
                self.redirect('_edit/%s' % title)


class ArticleEditorHandler(handler.TemplateHandler):
    """
    ArticleEditorHandler inherits from the hander.TemplateHandler class.
    It aggregates functionalities for creating, editing or persisting wiki articles to the datastore.
    """
    def render_article(self, logged=False, username=None, editionmode=False, article=None, error=""):
        self.render("article.html", logged=logged, username=username,
                    editionmode=editionmode, article=article, error=error)

    def get(self, article_title):
        username = None

        # do we have a logged in user?
        user_cookie = self.request.cookies.get('user')
        if user_cookie:
            username = security.check_secure_val(user_cookie)

            if username:
                # a known user is logged in
                # has he requested a particular article?
                title = article_title
                if title:
                    article = get_article(title)
                    if not article:
                        # creation of a new article with the presubmitted title
                        article = Article(title, "", "")
                else:
                    # creation of a new article without a presubmitted title
                    article = Article("", "", "")

                self.render_article(logged=True, username=username, editionmode=True, article=article)

        if not username:
            # only logged in users are allowed to create/edit articles
            self.redirect('/login')

    def post(self):
        # TODO: implement method
        pass


def get_article(title):
    """
    Return the article that corresponds to the given title
    :param title: input article title
    :return: the article that corresponds to the submitted title
    """
    article = None
    # search for the corresponding title from the memcache
    articles = memcache.get('top_ten')
    if articles and len(articles) > 0:
        for item in articles:
            if item.title == title:
                article = item
                break
    # in case the article we're looking for is not in memcache:
    if not article:
        # query the DB
        query = db.Query(Article)
        query.filter('title =', title)
        article = query.get()
    return article


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
