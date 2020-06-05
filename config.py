import pathlib
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    # Update interval
    GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 60000)  # 60 seconds TODO: change to 60seconds
    WEBAPP_TITLE = "Climate Change Datenstory"

    # PostgreSQL Parameters
    DB_PROVIDER = 'postgres'
    DB_HOST = 'localhost'
    DB_NAME = 'climate_change'
    DB_USER = 'fabianjordi'
    DB_PASSWORD = 'xagri8-vyndYw-qihpyq'
    DB_PORT = 5432

    # data_folder = '.' + os.sep + 'data'
    PATH = pathlib.Path(__file__).parent
    DATA_PATH = PATH.joinpath("data").resolve()

    SSL_REDIRECT = False

    """Flask configuration variables."""
    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')

    # Static Assets
    STATIC_FOLDER = os.environ.get('STATIC_FOLDER')
    TEMPLATES_FOLDER = os.environ.get('TEMPLATES_FOLDER')
    COMPRESSOR_DEBUG = os.environ.get('COMPRESSOR_DEBUG')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    FLASK_DEBUG = True
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class HerokuConfig(ProductionConfig):

    # PostgreSQL Parameters
    DB_PROVIDER = os.environ.get('DB_PROVIDER')
    DB_HOST = os.environ.get('DB_HOST')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_PORT = os.environ.get('DB_PORT')

    SSL_REDIRECT = True if os.environ.get('DYNO') else False

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # handle reverse proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class DockerConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'docker': DockerConfig,

    'default': DevelopmentConfig
}


