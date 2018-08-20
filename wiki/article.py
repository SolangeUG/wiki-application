import re
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
        user_cookie = self.request.cookies.get('user')
        if user_cookie:
            # do we have a logged in user?
            username = security.check_secure_val(user_cookie)
            logged = username is not None

            if logged:
                # do we have a non-empty title?
                if title:
                    article = get_article(title)
                    if article:
                        self.render_article(logged=logged, username=username, article=article)
                    else:
                        self.redirect('/_edit/%s' % title)
            else:
                # only logged in users are allowed to create/edit articles
                self.redirect('/login?from=%s' % self.request.url)
        else:
            # only logged in users are allowed to create/edit articles
            self.redirect('/login?from=%s' % self.request.url)


class NewArticleHandler(handler.TemplateHandler):
    """
    NewArticleHandler inherits from the hander.TemplateHandler class.
    It aggregates functionalities for creating and persisting new wiki articles to the datastore.
    """
    new_article = None

    def render_article(self, logged=False, username=None, editionmode=False, article=None, error="", newarticle=False):
        self.render("article.html", logged=logged, username=username, editionmode=editionmode, article=article,
                    error=error, newarticle=newarticle)

    def get(self):
        # do we have a logged in user?
        user_cookie = self.request.cookies.get('user')
        if user_cookie:
            username = security.check_secure_val(user_cookie)
            if username:
                # a known user is logged in
                global new_article
                new_article = Article(title=" ", content=" ", author=username)
                self.render_article(logged=True, username=username, editionmode=True,
                                    article=new_article, newarticle=True)
            else:
                # only logged in users are allowed to create/edit articles
                self.redirect('/login?from=%s' % self.request.url)
        else:
            # only logged in users are allowed to create/edit articles
            self.redirect('/login?from=%s' % self.request.url)

    def post(self):
        # retrieve the user currently logged in
        user_cookie = self.request.cookies.get('user')

        if user_cookie:
            username = security.check_secure_val(user_cookie)
            if username:
                title = self.request.get('title')
                content = self.request.get('content')

                if title and content:
                    new_article = Article(title=title, content=content, author=username)
                    new_article.put()

                    # rerun the DB query and update the cache
                    get_top_articles(True)

                    # self.redirect('/wiki/%s' % title)
                    self.redirect('/%s' % title)
                else:
                    # all mandatory fields haven't been filled
                    global new_article
                    if title:
                        new_article.title = title
                    if content:
                        new_article.content = content

                    error = "We need both a title and valid non-empty content!"
                    self.render_article(logged=True, username=username, editionmode=True,
                                        article=new_article, error=error, newarticle=True)
            else:
                # in case we don't have a valid username, redirect to login page
                self.redirect('/login?from=%s' % self.request.url)
        else:
            # in case we don't have a valid cookie
            self.redirect('/login?from=%s' % self.request.url)


class ArticleEditorHandler(handler.TemplateHandler):
    """
    ArticleEditorHandler inherits from the hander.TemplateHandler class.
    It aggregates functionalities for creating, editing or persisting wiki articles to the datastore.
    """
    known_article = None

    def render_article(self, logged=False, username=None, editionmode=False, article=None, error="", newarticle=False):
        self.render("article.html", logged=logged, username=username, editionmode=editionmode, article=article,
                    error=error, newarticle=newarticle)

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
                    global known_article
                    known_article = get_article(title)
                    if known_article:
                        # edition of an already existing article with the input title
                        self.render_article(logged=True, username=username, editionmode=True,
                                            article=known_article)
                    else:
                        # creation of a new article with the presubmitted title
                        known_article = Article(title=title, content=" ", author=username)
                        self.render_article(logged=True, username=username, editionmode=True,
                                            article=known_article, newarticle=True)
                else:
                    # creation of a new article without a presubmitted title
                    self.render_article(logged=True, username=username, editionmode=True, article=known_article)

        if not username:
            # only logged in users are allowed to create/edit articles
            self.redirect('/login?from=%s' % self.request.url)

    def post(self, article_title):
        # retrieve the user currently logged in
        user_cookie = self.request.cookies.get('user')

        if user_cookie:
            username = security.check_secure_val(user_cookie)
            if username:
                title = self.request.get('title')
                content = self.request.get('content')
                if not title:
                    title = article_title

                global known_article

                if title and content:
                    # update properties of edited article before saving
                    known_article.title = title
                    known_article.content = content
                    known_article.author = username
                    known_article.put()

                    # rerun the DB query and update the cache
                    get_top_articles(True)

                    # self.redirect('/wiki/%s' % title)
                    self.redirect('/%s' % title)
                else:
                    if title:
                        known_article.title = title
                    if content:
                        known_article.content = content
                    error = "We need both a title and valid non-empty content!"
                    self.render_article(logged=True, username=username, editionmode=True,
                                        article=known_article, error=error)
            else:
                # in case we don't have a valid username, redirect to login page
                self.redirect('/login?from=%s' % self.request.url)
        else:
            # in case we don't have a valid cookie
            self.redirect('/login?from=%s' % self.request.url)


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
            # workaround to remove all non-alphanumeric characters before comparison
            item_title = re.sub(r'\W', "", item.title)
            art_title = re.sub(r'\W', "", title)
            if item_title == art_title:
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
