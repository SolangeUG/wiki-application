import handler.handler as handler
from google.appengine.ext import db


class SignupHandler(handler.TemplateHandler):
    """
    UserHandler inherits from the hander.TemplateHandler class.
    It aggregates functionalities for signing up for an account.
    """
    def get(self):
        self.render("signup.html")

    def post(self):
        # TODO: fully implement this method
        pass


class LoginHandler(handler.TemplateHandler):
    """
    LoginHandler inherits from the hander.TemplateHandler class.
    It aggregates functionalities for logging into an account.
    """
    def get(self):
        self.render("login.html")

    def post(self):
        # TODO: fully implement this method
        pass


class LogoutHandler(handler.TemplateHandler):
    """
    LogoutHandler inherits from the hander.TemplateHandler class.
    It aggregates functionalities for logging out of an account.
    """
    def get(self):
        # TODO: fully implement this method
        self.redirect('/wiki')


class User(db.Model):
    """
    This class inherits from the GAE db.Model (entity) class, and represents a user account.
    A user account is made of the following properties:
        - username : the username chosen by the user
        - password : the hashed value of the password chosen by the user
        - email : the user's email address
        - comments : the user's comments upon account creation
        - created : creation date and time of user account
    """
    username = db.StringProperty(required=True, indexed=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()
    comments = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)