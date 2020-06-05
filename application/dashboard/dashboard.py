"""Instantiate a Dash app."""
import numpy as np
import pandas as pd
import os
import dash
import dash_table  # TODO: remove
from dash.dependencies import Input, Output, State, ClientsideFunction
import plotly.express as px
from .layout import html_layout, dash_layout
from ..models import db, db_session


gapminder = px.data.gapminder()

print(gapminder.head())

"""
    ### Parameter:
    Abkürzung|**Einheit**|**Beschreibung**
    :-----:|:-----:|:-----:
    gre000d0|W/m2|Globalstrahlung; Tagesmittel
    hto000d0|cm|Gesamtschneehöhe; Morgenmessung von 6 UTC
    nto000d0|%|Gesamtbewölkung; Tagesmittel
    prestad0|hPa|Luftdruck auf Stationshöhe (QFE); Tagesmittel
    rre150d0|mm|Niederschlag; Tagessumme 6 UTC - 6 UTC Folgetag
    sre000d0|min|Sonnenscheindauer; Tagessumme
    tre200d0|°C|Lufttemperatur 2 m über Boden; Tagesmittel
    tre200dn|°C|Lufttemperatur 2 m über Boden; Tagesminimum
    tre200dx|°C|Lufttemperatur 2 m über Boden; Tagesmaximum
    ure200d0|%|Relative Luftfeuchtigkeit 2 m über Boden; Tagesmittel
    """


@db_session
def get_data():
    query = db.select(
        """SELECT
            date,
            season,
            measured_value,
            altitude,
            latitude,
            longitude,
            abbr,
            ws.name,
            measurement_unit,
            cvd.name
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

                    WHERE (cvd.name = 'gre000m0'
                            OR cvd.name = 'hto000m0'
                            OR cvd.name = '')
                    AND (ws.abbr = 'BAS');""")

    return query


# Prepare DataFrame, filled with data from postgreSQL database
df = pd.DataFrame(get_data())

# rename columns
df.columns = ['date', 'season', 'value', 'altitude', 'latitude', 'longitude', 'station_abbr',
              'station_display_name', 'measurement_unit', 'name']

date_format = '%Y-%m-%d'
df['date'] = pd.to_datetime(df['date'], format=date_format)
df = df.set_index('date')
df.sort_index(inplace=True)

station = {}
# get stations coordinates
station.update({'altitude': df['altitude'].iloc[0]})
station.update({'latitude': df['latitude'].iloc[0]})
station.update({'longitude': df['longitude'].iloc[0]})


print(df.head())

stations = df.station_display_name.unique()

print(stations)


def create_dashboard(server):
    """Create a Plotly Dash dashboard."""

    assets_path = os.getcwd() + '/application/static/dist'

    print(assets_path)

    external_scripts = [
        {'src': 'https://www.google-analytics.com/analytics.js'},
    ]
    external_stylesheets = []

    mapbox_token = "pk.eyJ1IjoiZmFiaWFuam9yZGkiLCJhIjoiY2tiMTZyZml6MGV4NjJ5bzNvMXBlaGxhcyJ9.bSv6x4-2cCiaHqvccJDubw"

    geo_colors = [
        "#8dd3c7",
        "#ffd15f",
        "#bebada",
        "#fb8072",
        "#80b1d3",
        "#fdb462",
        "#b3de69",
        "#fccde5",
        "#d9d9d9",
        "#bc80bd",
        "#ccebc5",
    ]

    bar_coloway = [
        "#fa4f56",
        "#8dd3c7",
        "#ffffb3",
        "#bebada",
        "#80b1d3",
        "#fdb462",
        "#b3de69",
        "#fccde5",
        "#d9d9d9",
        "#bc80bd",
        "#ccebc5",
        "#ffed6f",
    ]

    dash_app = dash.Dash(server=server,
                    routes_pathname_prefix='/dashboard/',
                    external_scripts=external_scripts,
                    external_stylesheets=external_stylesheets,
                    assets_folder=assets_path,
                    assets_ignore='data-story*')


    # Custom HTML layout
    dash_app.index_string = html_layout

    # Create Layout
    interval = server.config['GRAPH_INTERVAL']
    dash_app.layout = dash_layout(interval)


    # Clientside callbacks
    dash_app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="resize"),
        Output('output-clientside', 'children'),
        [Input('input', 'value')]
    )

    # Initialize callbacks after app is loaded
    init_callbacks(dash_app)

    return dash_app.server


def init_callbacks(app):

    @app.callback(
        Output(component_id='graph', component_property='figure'),
        [Input('my-dropdown', 'value')]
    )
    def make_figure(selected_dropdown_value):
        return px.scatter(
            gapminder,
            x='gdpPercap',
            y='lifeExp',
            animation_frame='year',
            animation_group='country',
            size='pop',
            color='continent',
            hover_name="country",
            log_x=True,
            size_max=55,
            range_x=[100, 100000],
            range_y=[25, 90])
