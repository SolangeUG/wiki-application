import hmac
from pybcrypt import bcrypt

SECRET = "ThomasBeaudoin"


def hash_str(string):
    """
    Return the hashed value of a given string parameter.
    THe HMAC method is used to compute the hashed value.
    :param string: input parameter
    :return: the corresponding hashed value
    """
    return hmac.new(SECRET, string).hexdigest()


def make_secure_val(value):
    """
    Return the secure equivalent of a given value.
    :param value: input parameter
    :return: its equivalent secure value
    """
    return "%s|%s" % (value, hash_str(value))


def check_secure_val(hash_value):
    """
    Check that a hashed value is secure
    :param hash_value: input hashed value
    :return: True if it is secure
             False otherwise
    """
    value = hash_value.split('|')[0]
    if make_secure_val(value) == hash_value:
        return value


def hash_password(password):
    """
    Return the hashed equivalent of a password
    :param password: input password
    :return: equivalent encrypted value using the bcrypt algorithm
    """
    if password:
        return bcrypt.hashpw(password, bcrypt.gensalt())


def check_password(password, stored_hash_value):
    """
    Check if provided password is what is expected
    :param password: input password
    :param stored_hash_value:
    :return: True if the input value corresponds to what is expected
             False otherwise
    """
    hash_value = bcrypt.hashpw(password, stored_hash_value)
    return hash_value == stored_hash_value
