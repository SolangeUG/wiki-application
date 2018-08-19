import logging
from article import get_top_articles
import util.security as security
import handler.handler as handler

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
