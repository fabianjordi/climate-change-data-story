import pandas as pd
import datetime as dt
import numpy as np
import os
import math
import re
import requests
import urllib
import time
from bs4 import BeautifulSoup
from io import StringIO
import logging
from application.helpers import *
from pony import orm
from application.models import *
from application.config import *


def setup_climatic_variable_dimension_table():
    """
    Setup Variable dimensions table
    """

    variables_names_and_units = (
        {
            'display_name': 'Niederschlag',
            'name': 'precipitation',
            'measurement_unit': 'mm',
        }, {
            'display_name': 'Temperatur',
            'name': 'temperature',
            'measurement_unit': '°C',
        }
    )

    with orm.db_session:
        for variable in variables_names_and_units:
            cvd = ClimaticVariableDimension(**variable)
            orm.commit()


def import_meteoschweiz_homogene_messreihen_ab_1864():

    logging.info('Starting importing data of Meteo Schweiz (Homogene Messreihe ab 1864)…')

    try:
        # Get JSON of mapproducts
        url = 'https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html'
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        mapproduct_url = soup.find("div", {"id": "kartenprodukte-map"})['data-json-url']
        mapproduct_json_url = urllib.parse.urljoin(url, mapproduct_url)

        logging.info(mapproduct_json_url)

        # Interpret JSON
        s = requests.Session()
        s.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}

        res = s.get(mapproduct_json_url)
        res.encoding = 'ISO-8859-1'
        res.raise_for_status()
        data = res.json()
        stations_names = data['filters']['combinations']
        stations_names.remove('schweiz')  # remove 'schweiz' as it is the mean of all station data
        logging.info(stations_names)

        station_txt_url_pattern = data['assets']['documents']['files'][0]['filepattern']
        logging.info(station_txt_url_pattern)

        stations_urls_list = [urllib.parse.urljoin(url, station_txt_url_pattern.replace('[STATION]', station_url)) for
                              station_url in stations_names]

        with orm.db_session:

            # Read txt files of stations, one by one
            for i, station_txt_file in enumerate(stations_urls_list):

                logging.info(station_txt_file)
                res = s.get(station_txt_file)
                res.encoding = res.apparent_encoding
                lines = res.text.splitlines()

                ws_data = {}

                for j, line in enumerate(lines):

                    # Grab station informations and fill pandas dataFrame
                    # Get name
                    if line.startswith('Station:'):
                        name = line.split(':')[1].strip()
                        ws_data['name'] = name

                    # Get station altitude
                    if line.startswith('Altitude'):
                        altitude = float(re.sub("[^0-9.\-]", "", line.split(':')[1]))  # remove unit
                        ws_data['altitude'] = altitude

                    # Get station coordinates and convert them into longitude and latitude
                    if line.startswith('Coordinates:'):
                        coordinates = line.split(':')[1].split('/')
                        longitude = dms2dec(coordinates[0].strip())
                        latitude = dms2dec(coordinates[1].strip())
                        ws_data['longitude'] = longitude
                        ws_data['latitude'] = latitude

                    # Store the weather station
                    if ws_data.keys() >= {'name', 'longitude', 'latitude'}:
                        ws = WeatherStation(**ws_data)
                        ws_data.clear()

                    # Get date
                    if re.sub(' +', ' ', line).startswith('Year Month'):

                        # Grab climate facts (temperature and precipitation)
                        td_data = {}
                        cvd_data = {}
                        cf_data = {}

                        for k, linely in enumerate(lines[(j):]):

                            if k > 0:
                                linely = re.sub(' +', ';', linely)  # Remove multiple whitespace with semicolon
                                linely_items = linely.split(';')

                                # Generate date information
                                historic_date = dt.date(year=int(linely_items[0]), month=int(linely_items[1]), day=1)
                                # td_data['date'] = date
                                td_data['day'] = historic_date.day
                                td_data['week_number'] = historic_date.isocalendar()[1]
                                td_data['month'] = historic_date.month
                                td_data['season'] = get_season(historic_date)
                                td_data['year'] = historic_date.year

                                td = TimeDimension(
                                    # date=td_data['date'],
                                    day=td_data['day'],
                                    week_number=td_data['week_number'],
                                    month=td_data['month'],
                                    season=td_data['season'],
                                    year=td_data['year']
                                )

                                for m, item in enumerate(linely_items):

                                    # Temperature
                                    if m == 2:
                                        cf_data['temperature'] = linely_items[2]

                                        try:
                                            cf = ClimaticFacts(
                                                measured_value=float(cf_data['temperature']),
                                                weather_station=ws,
                                                time_dimension=td,
                                                climatic_variable_dimension=2,
                                            )
                                        except ValueError:
                                            logging.warning('Temperature value is not of type float')

                                    # Precipitation
                                    if m == 3:
                                        cf_data['precipitation'] = linely_items[3]

                                        try:
                                            cf = ClimaticFacts(
                                                measured_value=float(cf_data['precipitation']),
                                                weather_station=ws,
                                                time_dimension=td,
                                                climatic_variable_dimension=1,
                                            )
                                        except ValueError:
                                            logging.warning('Precipitation value is not of type float')
                        orm.commit()
                        break

        logging.info('Finished importing data of Meteo Schweiz (Homogene Messreihe ab 1864)')

    except requests.exceptions.HTTPError as e:
        logging.error(e)


orm.set_sql_debug(config.sql_debug)
db.bind(**config.db_params)
db.generate_mapping(create_tables=True)
db.drop_all_tables(with_all_data=True)
db.create_tables()

setup_climatic_variable_dimension_table()
import_meteoschweiz_homogene_messreihen_ab_1864()

db.disconnect()
