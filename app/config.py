"""Flask config class."""
from os.path import dirname, abspath, join


class Config(object):
    """Set Flask base configuration"""
    SECRET_KEY = 'dfdQbTOExternjy5xmCNaA'

    # General Config
    DEBUG = False
    TESTING = False

    # Forms config
    WTF_CSRF_SECRET_KEY = 'this-is-not-random-but-it-should-be'

    # Database config
    CWD = dirname(abspath(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(CWD, 'musicians.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    DEBUG = False
    TESTING = False


class TestConfig(Config):
    DEBUG = True
    TESTING = True
    #  In memory database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    #  To allow forms to be submitted from the tests without the CSRF token
    WTF_CSRF_ENABLED = False


class DevConfig(Config):
    DEBUG = True
