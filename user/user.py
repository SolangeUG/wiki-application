import logging
import handler.handler as handler
import util.security as security
import util.validator as validator
from google.appengine.ext import db

# log user related activities
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class SignupHandler(handler.TemplateHandler):
    """
    UserHandler inherits from the hander.TemplateHandler class.
    It aggregates functionalities for signing up for an account.
    """
    def get(self):
        self.render("signup.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        cfpassword = self.request.get('verify')
        user_email = self.request.get('email')
        comments = self.request.get('text')

        if validator.validate_user(username, password, cfpassword, user_email):

            # check if the input username is unique
            query = db.Query(User)
            query.filter('username =', username)
            existing_user = query.get()

            if existing_user:
                # ask the user to choose a different username
                username_error = "Username already exists"
                self.render("signup.html", username=username, username_error=username_error)
            else:
                # create and persist an account for the user
                hashed_password = security.hash_password(password)
                new_user = User(username=username, password=hashed_password, email=user_email, comments=comments)
                key = new_user.put()

                # log new user account key
                logging.warn('USER | Created user key %s' % str(key))

                self.response.headers['Content-Type'] = 'text/plain'
                # set a cookie with the username
                user_cookie = security.make_secure_val(username)
                self.response.set_cookie('user', str(user_cookie), max_age=7200, path='/')
                self.redirect('/wiki')

        else:
            username_error = ""
            password_error = ""
            cfpassword_error = ""
            email_error = ""

            if not validator.is_username_valid(username):
                username_error = "Invalid username!"
            if not validator.is_password_valid(password):
                password_error = "Invalid password!"
            if not validator.is_cfpassword_valid(password, cfpassword):
                cfpassword_error = "Your passwords don't match!"
            if not validator.is_email_valid(user_email):
                email_error = "Invalid email!"
            self.render("signup.html",
                        username=username,
                        username_error=username_error,
                        password_error=password_error,
                        cfpassword_error=cfpassword_error,
                        email=user_email,
                        email_error=email_error,
                        comments=comments)


class LoginHandler(handler.TemplateHandler):
    """
    LoginHandler inherits from the hander.TemplateHandler class.
    It aggregates functionalities for logging into an account.
    """
    def get(self):
        self.render("login.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        if username and password:
            # retrieve user from the datastore
            query = db.Query(User)
            query.filter('username =', username)
            user = query.get()

            if user:
                # verify input password
                if security.check_password(password, user.password):
                    self.response.headers['Content-Type'] = 'text/plain'

                    # set a cookie with the username
                    user_cookie = security.make_secure_val(user.username)
                    self.response.set_cookie('user', str(user_cookie), max_age=7200, path='/')

                    # redirect the user to where they came from
                    host = self.request.headers.get('Host')
                    referer = self.request.headers.get('Referer')
                    if referer and host:
                        # the referer URL is of the form: protocol://host/original_path
                        # so, the orginal relative path becomes:
                        original_path = referer.split(host)[1]
                        logging.warn("LOGIN PAGE | Path to requested resource: %s" % original_path)

                        self.redirect(original_path)
                    else:
                        # default redirect
                        self.redirect("/wiki")
                else:
                    # the input password is not valid
                    message = "Invalid password!"
                    self.render("login.html", password_error=message)
            else:
                # the input username is unknown
                message = "Invalid username!"
                self.render("login.html", username_error=message)
        else:
            # no username or password were input
            self.render("login.html", username_error="Please input valid usename!",
                        password_error="Please input valid password!")


class LogoutHandler(handler.TemplateHandler):
    """
    LogoutHandler inherits from the hander.TemplateHandler class.
    It aggregates functionalities for logging out of an account.
    """
    def get(self):
        # clear out any user cookie that might have been set
        self.response.headers.add_header('Set-Cookie', 'user=%s; Path=/' % str())
        # all we ever do from here is go back to the general wiki page
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