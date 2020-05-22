#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import required libraries
from application.config import *
from application.importer import *
import logging
# from pony import orm
# from application.models import db
# from your_favorite_web_framework import App


#config = Config()
# logging.basicConfig(level=config.logging_level)

# Import all the data from different sources
#import_meteoschweiz_homogene_messreihen_ab_1864(config)




# Main
if __name__ == "__main__":
    logging.info('Start app…')

    # app.run(debug=True)

    logging.info('App started')
    #app = App()
    #app.run()
