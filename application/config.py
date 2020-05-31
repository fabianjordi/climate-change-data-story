import os
import pathlib
import logging


class Config(object):
    # PostgreSQL Parameters
    db_params = {
        'provider': 'postgres',
        'host': 'localhost',
        'database': 'climate_change',
        'user': 'fabianjordi',
        'password': 'xagri8-vyndYw-qihpyq',
    }

    # Update interval
    GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 60000)  # 60 seconds TODO: change to 60seconds
    WEBAPP_TITLE = "Climate Change Data Story"

    # data_folder = '.' + os.sep + 'data'
    PATH = pathlib.Path(__file__).parent
    DATA_PATH = PATH.joinpath("data").resolve()

    def get_db_params(self):
        return self.db_params

    def get_data_folder(self):
        return self.DATA_PATH


class ProductionConfig(Config):
    DEBUG = False
    SQL_DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQL_DEBUG = True
    logging.basicConfig(level=logging.DEBUG)


config = DevelopmentConfig()


