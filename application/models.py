from datetime import date
from pony.orm import *
from config import *


db = Database()


class ClimaticFacts(db.Entity):
    id = PrimaryKey(int, auto=True)
    measured_value = Optional(float)
    time_dimension = Required('TimeDimension')
    climatic_variable_dimension = Required('ClimaticVariableDimension')
    weather_station = Optional('WeatherStation')


class ClimaticVariableDimension(db.Entity):
    id = PrimaryKey(int, auto=True)
    display_name = Required(str)
    name = Required(str, unique=True)
    measurement_unit = Optional(str)
    climatic_facts = Set(ClimaticFacts)


class WeatherStation(db.Entity):
    id = PrimaryKey(int, auto=True)
    altitude = Optional(float)
    latitude = Required(float)
    longitude = Required(float)
    name = Required(str)
    abbr = Required(str, 16, unique=True)
    climatic_facts = Set(ClimaticFacts)


class TimeDimension(db.Entity):
    id = PrimaryKey(int, auto=True)
    date = Required(date)
    day = Optional(int)
    week_number = Optional(int)
    month = Optional(int)
    season = Optional(int)
    year = Optional(int)
    climatic_facts = Set(ClimaticFacts)


def setup(config_name):
    """ Set up the database """
    # db.bind(**database_config, create_db=True)
    # db.generate_mapping(create_tables=True)
    db.bind(**config[config_name].DB_PARAMS)
    db.generate_mapping()
    print(db)
    print(db_session)
