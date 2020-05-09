import os
import pathlib
import logging


class Config:
    # PostgreSQL Parameters
    db_params = {
        'provider': 'postgres',
        'host': 'localhost',
        'database': 'climatechange',
        'user': 'fabianjordi',
        'password': 'xagri8-vyndYw-qihpyq',
    }

    logging.basicConfig(level=logging.DEBUG)
    sql_debug = False

    # Update interval
    GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 60000)  # 60 seconds TODO: change to 60seconds
    WEBAPP_TITLE = "Wetterstation für SeglerInnen"

    # data_folder = '.' + os.sep + 'data'
    PATH = pathlib.Path(__file__).parent
    DATA_PATH = PATH.joinpath("data").resolve()

    def get_db_params(self):
        return self.db_params

    def get_data_folder(self):
        return self.DATA_PATH


config = Config()


