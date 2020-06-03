"""Compile static src."""
from flask import current_app as app
from flask_assets import Bundle
from webassets.filter import get_filter


def compile_static_assets(assets):
    """
    Compile stylesheets if in development mode.
    :param assets: Flask-Assets Environment
    :type assets: Environment
    """
    assets.auto_build = True
    assets.debug = False

    libsass = get_filter(
        'libsass',
        as_output=True,
        style='compressed',
    )

    scss_datastory_bundle = Bundle(
                                'src/scss/global.scss',
                                'src/scss/data-story.scss',
                                filters=libsass,
                                output='dist/css/data-story.css',
                                extra={'rel': 'stylesheet/scss'}
    )

    scss_dashboard_bundle = Bundle(
                                'src/scss/global.scss',
                                'src/scss/dashboard.scss',
                                filters=libsass,
                                output='dist/css/dashboard.css',
                                extra={'rel': 'stylesheet/scss'}
    )

    assets.register('scss_datastory', scss_datastory_bundle)
    assets.register('scss_dashboard', scss_dashboard_bundle)

    if app.config['FLASK_ENV'] == 'development':
        scss_datastory_bundle.build()
        scss_dashboard_bundle.build()

    return assets
