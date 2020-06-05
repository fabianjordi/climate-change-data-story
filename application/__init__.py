"""Initialize Flask app"""
from flask import Flask
from flask_assets import Environment
from application.models import *
from .models import *


def create_app(config_name):
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)
    # app.config.from_object('config.Config')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    assets = Environment()
    assets.init_app(app)

    # setup db connection and schema
    setup(config_name)

    with app.app_context():

        # Import parts of our core Flask app
        from . import routes
        from .assets import compile_static_assets

        # Import Dash application
        from .dashboard.dashboard import create_dashboard

        app = create_dashboard(app)

        # Compile static src
        compile_static_assets(assets)

        return app
