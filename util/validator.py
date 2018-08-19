import re

PASSWORD_RE = re.compile(r"^.{3,20}$")
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")


def is_username_valid(username):
    """
    Validate an input username against a regular expression
    :param username: input username
    :return: true if the username verifies, false otherwise
    """
    return username and USER_RE.match(username)


def is_password_valid(password):
    """
    Validate an input password against a regular expression
    :param password: input password
    :return: true if the password verifies, false otherwise
    """
    return password and PASSWORD_RE.match(password)


def is_cfpassword_valid(password, cfpassword):
    """
    Validate an input password and its confirmation against a regular expression
    :param password: input password
    :param cfpassword: confirmed password
    :return: the result of the verification
    """
    result = False
    if is_password_valid(password):
        result = password == cfpassword
    return result


def is_email_valid(email):
    """
    Validate an input email against a regular expression
    :param email: input email
    :return: true if the email verifies, false otherwise
    """
    return not email or EMAIL_RE.match(email)


def validate_user(username, password, cfpassword, email):
    """
    Validate user input information
    :param username: input username
    :param password: input password
    :param cfpassword: confirmed password
    :param email: inoput email
    :return: true if all the information is valid, false otherwise
    """
    result = is_username_valid(username) and is_password_valid(password)
    result = result and is_cfpassword_valid(password, cfpassword)
    result = result and is_email_valid(email)
    return result
