from datetime import date
from pony.orm import *


db = Database()


class ClimaticFacts(db.Entity):
    id = PrimaryKey(int, auto=True)
    measured_value = Optional(float)
    weather_station = Required('WeatherStation')
    time_dimension = Required('TimeDimension')
    climatic_variable_dimension = Required('ClimaticVariableDimension')


class ClimaticVariableDimension(db.Entity):
    id = PrimaryKey(int, auto=True)
    display_name = Required(str)
    name = Required(str)
    measurement_unit = Optional(str)
    climatic_facts = Set(ClimaticFacts)


class WeatherStation(db.Entity):
    id = PrimaryKey(int, auto=True)
    altitude = Optional(float)
    latitude = Required(float)
    longitude = Required(float)
    name = Required(str)
    climatic_facts = Set(ClimaticFacts)


class TimeDimension(db.Entity):
    id = PrimaryKey(int, auto=True)
    day = Optional(int)
    week_number = Optional(int)
    month = Optional(int)
    season = Optional(int)
    year = Optional(int)
    climatic_facts = Set(ClimaticFacts)
