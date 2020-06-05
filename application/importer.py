import pandas as pd
import requests
import urllib
from bs4 import BeautifulSoup
import posixpath
from application.helpers import *
from pony import orm
from application.models import *
from config import *
import logging


config = config[os.getenv('FLASK_ENV') or 'default']


def setup_climatic_variable_dimension_table():
    """
    Setup Variable dimensions table
    """

    variables_names_and_units = (
        {
            'display_name': 'Globalstrahlung (Monatsmittel)',
            'name': 'gre000m0',
            'measurement_unit': 'W / m≤',
        }, {
            'display_name': 'Gesamtschneehöhe (Monatsmittel)',
            'name': 'hto000m0',
            'measurement_unit': 'cm',
        }, {
            'display_name': 'Gesamtbewölkung (Monatsmittel)',
            'name': 'nto000m0',
            'measurement_unit': '%',
        }, {
            'display_name': 'Luftdruck auf Stationshöhe (QFE, Monatsmittel)',
            'name': 'prestam0',
            'measurement_unit': 'hPa',
        }, {
            'display_name': 'Niederschlag (Monatssumme)',
            'name': 'rre150m0',
            'measurement_unit': 'mm',
        }, {
            'display_name': 'Sonnenscheindauer (Monatssumme)',
            'name': 'sre000m0',
            'measurement_unit': 'min',
        }, {
            'display_name': 'Lufttemperatur 2m über Boden (Monatsmittel)',
            'name': 'tre200m0',
            'measurement_unit': '°C',
        }, {
            'display_name': 'Lufttemperatur 2m über Boden (absolutes Monatsminimum)',
            'name': 'tre200mn',
            'measurement_unit': '°C',
        }, {
            'display_name': 'Lufttemperatur 2m über Boden (absolutes Monatsmaximum)',
            'name': 'tre200mx',
            'measurement_unit': '°C',
        }, {
            'display_name': 'Relative Luftfeuchtigkeit 2m über Boden (Monatsmittel)',
            'name': 'ure200m0',
            'measurement_unit': '%',
        }
    )

    with orm.db_session:
        for variable in variables_names_and_units:
            cvd = ClimaticVariableDimension(**variable)
            orm.commit()


def import_swiss_weather_stations():

    logging.info('Start importing swiss weather stations …')

    file = posixpath.join(config.DATA_PATH, "stations_CH2018_meta.csv")
    # STATION_NAME,NAT_ABBR,LATITUDE,LONGITUDE,XCOORD,YCOORD,ELEVATION
    column_names = ['name', 'abbr', 'latitude', 'longitude', 'xcoord', 'ycoord', 'altitude']
    df = pd.read_csv(file, delimiter=',', header=0, names=column_names)

    ws_data = {}

    with orm.db_session:
        for row in df.itertuples():
            ws_data['name'] = row.name
            ws_data['abbr'] = row.abbr
            ws_data['latitude'] = row.latitude
            ws_data['longitude'] = row.longitude
            ws_data['altitude'] = row.altitude

            ws = WeatherStation(**ws_data)
            ws_data.clear()
            orm.commit()

    logging.info('Finished importing swiss weather stations.')


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

        station_txt_url_pattern = data['src']['documents']['files'][0]['filepattern']
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

                    # Grab station informations
                    # Get name
                    if line.startswith('Station:'):
                        name = line.split(':')[1].strip()
                        ws_data['abbr'] = stations_names[i]
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
                    if ws_data.keys() >= {'abbr', 'name', 'longitude', 'latitude'}:

                        ws = WeatherStation.get(abbr=ws_data['abbr'])
                        if ws is None:
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
                                td_data['date'] = historic_date
                                td_data['day'] = historic_date.day
                                td_data['week_number'] = historic_date.isocalendar()[1]
                                td_data['month'] = historic_date.month
                                td_data['season'] = get_season(historic_date)
                                td_data['year'] = historic_date.year

                                td = TimeDimension(
                                    date=td_data['date'],
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
                                            cvd = ClimaticVariableDimension.get(name='tre200m0')

                                            cf = ClimaticFacts(
                                                measured_value=float(cf_data['temperature']),
                                                weather_station=ws,
                                                time_dimension=td,
                                                climatic_variable_dimension=cvd.id,
                                            )
                                        except ValueError:
                                            logging.warning('Temperature value is not of type float')

                                    # Precipitation
                                    if m == 3:
                                        cf_data['precipitation'] = linely_items[3]

                                        try:
                                            cvd = ClimaticVariableDimension.get(name='rre150m0')

                                            cf = ClimaticFacts(
                                                measured_value=float(cf_data['precipitation']),
                                                weather_station=ws,
                                                time_dimension=td,
                                                climatic_variable_dimension=cvd.id,
                                            )
                                        except ValueError:
                                            logging.warning('Precipitation value is not of type float')
                        orm.commit()
                        break

        # db.flush()
        logging.info('Finished importing data of Meteo Schweiz (Homogene Messreihe ab 1864)')

    except requests.exceptions.HTTPError as e:
        logging.error(e)


def import_nbcn_monthly_values():
    """
    NBCN monthly values

    1864-2018   https://data.geo.admin.ch/ch.meteoschweiz.klima/nbcn-monatswerte/NBCN-m_1864-2018.csv
    2019        https://data.geo.admin.ch/ch.meteoschweiz.klima/nbcn-monatswerte/NBCN-m.csv
    """
    logging.info('Start importing NBCN monthly data …')

    files = [
        {
            'path': 'nbcn/nbcn-monatswerte/NBCN-m.csv',
            'timeframe': '2019',
            'timeformat': '%Y%m',
            'skiprows': 1,
        }, {
            'path': 'nbcn/nbcn-monatswerte/NBCN-m_1864-2018.csv',
            'timeframe': '1864-2018',
            'timeformat': '%Y%m%d',
            'skiprows': 0,
        }
    ]

    for file in files:

        file_path = posixpath.join(config.DATA_PATH, file['path'])
        # column_names = ['stn', 'time', 'gre000m0', 'hto000m0', 'nto000m0', 'prestam0', 'rre150m0', 'sre000m0', 'tre200m0', 'tre200mn', 'tre200mx', 'ure200m0']
        df = pd.read_csv(file_path, delimiter=';', skiprows=file['skiprows'], header=0)
        df = df.dropna()
        print(df)
        df = df[df.stn.str.contains('stn') == False] # Remove multiple repeating headers


        # print(df.columns.values)

        td_data = {}
        cf_data = {}

        with orm.db_session:
            for row in df.itertuples():
                print('row', row)
                historic_date = dt.datetime.strptime(str(row.time), file['timeformat'])
                print('historic_date', historic_date)
                td_data['date'] = historic_date
                td_data['day'] = historic_date.day
                td_data['week_number'] = historic_date.isocalendar()[1]
                td_data['month'] = historic_date.month
                td_data['season'] = get_season(historic_date)
                td_data['year'] = historic_date.year

                td = TimeDimension.get(date=historic_date)
                if td is None:
                    td = TimeDimension(**td_data)
                    orm.commit()

                ws = WeatherStation.get(abbr=row.stn)

                # - = empty value
                if row.gre000m0 != '-':
                    cvd = ClimaticVariableDimension.get(name='gre000m0')

                    cf_data['measured_value'] = row.gre000m0
                    cf_data['time_dimension'] = td.id
                    cf_data['climatic_variable_dimension'] = cvd.id
                    cf_data['weather_station'] = ws.id
                    cf = ClimaticFacts(**cf_data)
                    orm.commit()

                if row.hto000m0 != '-':
                    cvd = ClimaticVariableDimension.get(name='hto000m0')

                    cf_data['measured_value'] = row.hto000m0
                    cf_data['time_dimension'] = td.id
                    cf_data['climatic_variable_dimension'] = cvd.id
                    cf_data['weather_station'] = ws.id
                    cf = ClimaticFacts(**cf_data)
                    orm.commit()

                if row.nto000m0 != '-':
                    cvd = ClimaticVariableDimension.get(name='nto000m0')

                    cf_data['measured_value'] = row.nto000m0
                    cf_data['time_dimension'] = td.id
                    cf_data['climatic_variable_dimension'] = cvd.id
                    cf_data['weather_station'] = ws.id
                    cf = ClimaticFacts(**cf_data)
                    orm.commit()

                if row.prestam0 != '-':
                    cvd = ClimaticVariableDimension.get(name='prestam0')

                    cf_data['measured_value'] = row.prestam0
                    cf_data['time_dimension'] = td.id
                    cf_data['climatic_variable_dimension'] = cvd.id
                    cf_data['weather_station'] = ws.id
                    cf = ClimaticFacts(**cf_data)
                    orm.commit()

                if row.rre150m0 != '-':
                    cvd = ClimaticVariableDimension.get(name='rre150m0')

                    cf_data['measured_value'] = row.rre150m0
                    cf_data['time_dimension'] = td.id
                    cf_data['climatic_variable_dimension'] = cvd.id
                    cf_data['weather_station'] = ws.id
                    cf = ClimaticFacts(**cf_data)
                    orm.commit()

                if row.sre000m0 != '-':
                    cvd = ClimaticVariableDimension.get(name='sre000m0')

                    cf_data['measured_value'] = row.sre000m0
                    cf_data['time_dimension'] = td.id
                    cf_data['climatic_variable_dimension'] = cvd.id
                    cf_data['weather_station'] = ws.id
                    cf = ClimaticFacts(**cf_data)
                    orm.commit()

                if row.tre200m0 != '-':
                    cvd = ClimaticVariableDimension.get(name='tre200m0')

                    cf_data['measured_value'] = row.tre200m0
                    cf_data['time_dimension'] = td.id
                    cf_data['climatic_variable_dimension'] = cvd.id
                    cf_data['weather_station'] = ws.id
                    cf = ClimaticFacts(**cf_data)
                    orm.commit()

                if row.tre200mn != '-':
                    cvd = ClimaticVariableDimension.get(name='tre200mn')

                    cf_data['measured_value'] = row.tre200mn
                    cf_data['time_dimension'] = td.id
                    cf_data['climatic_variable_dimension'] = cvd.id
                    cf_data['weather_station'] = ws.id
                    cf = ClimaticFacts(**cf_data)
                    orm.commit()

                if row.tre200mx != '-':
                    cvd = ClimaticVariableDimension.get(name='tre200mx')

                    cf_data['measured_value'] = row.tre200mx
                    cf_data['time_dimension'] = td.id
                    cf_data['climatic_variable_dimension'] = cvd.id
                    cf_data['weather_station'] = ws.id
                    cf = ClimaticFacts(**cf_data)
                    orm.commit()

                if row.ure200m0 != '-':
                    cvd = ClimaticVariableDimension.get(name='ure200m0')

                    cf_data['measured_value'] = row.ure200m0
                    cf_data['time_dimension'] = td.id
                    cf_data['climatic_variable_dimension'] = cvd.id
                    cf_data['weather_station'] = ws.id
                    cf = ClimaticFacts(**cf_data)
                    orm.commit()

    # db.flush()
    logging.info('Finished importing NBCN monthly data.')


if __name__ == '__main__':

    """if ClimaticFacts.select().first() is None:
        populate_database()"""

    orm.set_sql_debug(config.DEBUG)
    db.bind(
        provider=config.DB_PROVIDER,
        host=config.DB_HOST,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        port=config.DB_PORT,
    )
    db.generate_mapping(create_tables=True)
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    # Setup and imports
    setup_climatic_variable_dimension_table()

    import_swiss_weather_stations()

    # No need importing the following data since data is already stored in the dababase
    # import_meteoschweiz_homogene_messreihen_ab_1864()

    import_nbcn_monthly_values()

    db.disconnect()
