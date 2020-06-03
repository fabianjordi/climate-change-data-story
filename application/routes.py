"""Core Flask app routes."""
from flask import render_template, jsonify
from flask import current_app as app
from .models import *


def get_json(data):
    response = app.response_class(
        response=data,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/')
@app.route('/index')
def home():
    """Landing page."""
    return render_template(
        'index.jinja2',
        title='Plotly Dash Flask Tutorial',
        description='Embed Plotly Dash into your Flask applications.',
        template='home-template',
        body="This is a homepage served with Flask."
    )


@app.route('/getWeatherStations')
@db_session
def get_weather_stations():
    with db.set_perms_for(WeatherStation):
        perm('view')
        weather_stations = select(ws for ws in WeatherStation).order_by(WeatherStation.name)[:]

    return jsonify([ws.to_dict() for ws in weather_stations])


@app.route('/getTemperatures')
@db_session
def get_temperatures():
    with db.set_perms_for(ClimaticFacts, ClimaticVariableDimension, TimeDimension, WeatherStation):
        perm('view')

        """climatic_facts = select((td.date, td.year, cf.measured_value, cvd.measurement_unit, ws.name)
                                for cf in ClimaticFacts
                                for td in cf.time_dimension
                                for ws in cf.weather_station
                                for cvd in cf.climatic_variable_dimension
                                if (ws.name == 'Basel / Binningen' and cvd.name == 'temperature'))[:]"""

        climatic_facts = db.select("""SELECT JSON_AGG(t)
                                        FROM (
                                            SELECT 
                                                date,
                                                year,
                                                month,
                                                measured_value,
                                                ws.name
                                            FROM timedimension AS td
                                                INNER JOIN
                                                climaticfacts AS cf
                                                ON td.id = cf.time_dimension
                                                    INNER JOIN
                                                    weatherstation AS ws
                                                    ON ws.id = cf.weather_station
                                                        INNER JOIN
                                                        climaticvariabledimension AS cvd
                                                        ON cvd.id = cf.climatic_variable_dimension
                                            WHERE ws.abbr = 'BAS' 
                                            AND cvd.name = 'tre200m0') t""")

    return get_json(climatic_facts)


@app.route('/getAverageMonthTemperatures')
@db_session
def get_average_month_temperatures2():
    with db.set_perms_for(ClimaticFacts, ClimaticVariableDimension, TimeDimension, WeatherStation):
        perm('view')

        climatic_facts = db.select("""SELECT JSON_AGG(t)
                                        FROM (
                                            SELECT 
                                                date,
                                                ROUND(AVG(measured_value)::numeric,2) AS value
                                            FROM timedimension AS td
                                                INNER JOIN
                                                climaticfacts AS cf
                                                ON td.id = cf.time_dimension
                                                    INNER JOIN
                                                    climaticvariabledimension AS cvd
                                                    ON cvd.id = cf.climatic_variable_dimension
                                                        INNER JOIN
                                                        weatherstation AS ws
                                                        ON ws.id = cf.weather_station
                                            WHERE cvd.name = 'tre200m0' 
                                                AND EXTRACT(MONTH FROM date) = 7
                                                AND EXTRACT(YEAR FROM date) != date_part('year', CURRENT_DATE)
                                                AND EXTRACT(YEAR FROM date) >= 1864
                                                AND ws.altitude < 800
                                            /*AND td.year != date_part('year', CURRENT_DATE)*/
                                            GROUP BY td.date, td.year, td.month
                                            ORDER BY td.year) t""")

    return get_json(climatic_facts)


@app.route('/getAverageTemperatures')
@db_session
def get_average_temperatures():
    with db.set_perms_for(ClimaticFacts, ClimaticVariableDimension, TimeDimension, WeatherStation):
        perm('view')

        climatic_facts = db.select("""SELECT JSON_AGG(t)
                                        FROM (
                                            SELECT 
                                                year,
                                                ROUND(AVG(measured_value)::numeric,2) AS value
                                            FROM timedimension AS td
                                                INNER JOIN
                                                climaticfacts AS cf
                                                ON td.id = cf.time_dimension
                                                    INNER JOIN
                                                    climaticvariabledimension AS cvd
                                                    ON cvd.id = cf.climatic_variable_dimension
                                            WHERE cvd.name = 'tre200m0'
                                                AND td.year != date_part('year', CURRENT_DATE)
                                                AND EXTRACT(YEAR FROM date) >= 1864
                                            GROUP BY td.year
                                            ORDER BY td.year) t""")

    return get_json(climatic_facts)


@app.route('/getTemperaturesPerMonthAndYear')
@db_session
def get_temperatures_per_month_and_year():
    with db.set_perms_for(ClimaticFacts, ClimaticVariableDimension, TimeDimension, WeatherStation):
        perm('view')

        climatic_facts = db.select("""SELECT JSON_AGG(t)
                                        FROM (
                                            SELECT 
                                                date,
                                                month,
                                                ROUND(AVG(measured_value)::numeric,2) AS value
                                            FROM timedimension AS td
                                                INNER JOIN
                                                climaticfacts AS cf
                                                ON td.id = cf.time_dimension
                                                    INNER JOIN
                                                    climaticvariabledimension AS cvd
                                                    ON cvd.id = cf.climatic_variable_dimension
                                                        INNER JOIN
                                                        weatherstation AS ws
                                                        ON ws.id = cf.weather_station
                                            WHERE cvd.name = 'tre200m0' 
                                                AND EXTRACT(MONTH FROM date) < 13
                                                AND EXTRACT(YEAR FROM date) != date_part('year', CURRENT_DATE)
                                                AND EXTRACT(YEAR FROM date) >= 1864
                                                AND ws.altitude < 900
                                                AND ws.altitude > 200
                                            GROUP BY td.date, td.month
                                            ORDER BY td.date) t""")

    return get_json(climatic_facts)